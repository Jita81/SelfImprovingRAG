from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict, Counter

from src.models.validation_result import ValidationResult

@dataclass
class Pattern:
    """Represents a detected pattern in validation issues"""
    pattern_type: str  # "semantic" or "temporal"
    description: str
    significance: float
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    related_issues: List[str]
    metadata: Dict[str, Any]

class PatternRecognitionService:
    """Service for detecting patterns in validation issues"""
    
    def __init__(self, embedding_model):
        """Initialize with an embedding model for semantic analysis"""
        self.embedding_model = embedding_model
        self.min_sequence_length = 2
        self.min_sequence_occurrences = 3
        self.eps = 0.5  # DBSCAN clustering parameter
        self.min_samples = 2  # DBSCAN clustering parameter
    
    def analyze_validation_history(
        self,
        validation_results: List[ValidationResult],
        min_significance: float = 0.3
    ) -> List[Pattern]:
        """Analyze validation history for patterns"""
        if not validation_results:
            return []
        
        patterns = []
        
        # Find semantic patterns using clustering
        semantic_patterns = self._find_semantic_patterns(validation_results)
        patterns.extend(semantic_patterns)
        
        # Find temporal patterns using sequence analysis
        temporal_patterns = self._find_temporal_patterns(validation_results)
        patterns.extend(temporal_patterns)
        
        # Filter by significance threshold
        patterns = [p for p in patterns if p.significance >= min_significance]
        
        return patterns
    
    def _find_semantic_patterns(
        self,
        validation_results: List[ValidationResult]
    ) -> List[Pattern]:
        """Find semantically similar issues using clustering"""
        # Extract all unique issues
        all_issues = []
        issue_to_results = defaultdict(list)
        
        for result in validation_results:
            for issue in result.issues:
                if issue not in all_issues:
                    all_issues.append(issue)
                issue_to_results[issue].append(result)
        
        if not all_issues:
            return []
        
        # Get embeddings for issues
        embeddings = self.embedding_model.encode(all_issues)
        
        # Cluster issues using DBSCAN
        clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        cluster_labels = clustering.fit_predict(embeddings)
        
        patterns = []
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Skip noise points
                continue
            
            # Get issues in this cluster
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_issues = [all_issues[i] for i in cluster_indices]
            
            # Calculate cluster metadata
            cluster_embeddings = embeddings[cluster_indices]
            centroid = np.mean(cluster_embeddings, axis=0)
            similarities = np.dot(cluster_embeddings, centroid)
            avg_similarity = float(np.mean(similarities))
            
            # Get timestamps for cluster issues
            timestamps = []
            for issue in cluster_issues:
                timestamps.extend(r.timestamp for r in issue_to_results[issue])
            
            pattern = Pattern(
                pattern_type="semantic",
                description=f"Similar issues: {', '.join(cluster_issues)}",
                significance=self._calculate_semantic_significance(
                    len(cluster_issues),
                    avg_similarity,
                    len(validation_results)
                ),
                occurrences=len(cluster_issues),
                first_seen=min(timestamps),
                last_seen=max(timestamps),
                related_issues=cluster_issues,
                metadata={
                    "cluster_size": len(cluster_issues),
                    "average_similarity": avg_similarity
                }
            )
            patterns.append(pattern)
        
        return patterns
    
    def _find_temporal_patterns(
        self,
        validation_results: List[ValidationResult]
    ) -> List[Pattern]:
        """Find temporal patterns in issue sequences"""
        if len(validation_results) < self.min_sequence_length:
            return []
        
        # Sort results by timestamp
        sorted_results = sorted(validation_results, key=lambda x: x.timestamp)
        
        # Generate sequences of different lengths
        patterns = []
        for seq_len in range(self.min_sequence_length, len(sorted_results) // 2 + 1):
            sequences = self._extract_sequences(sorted_results, seq_len)
            sequence_counts = Counter()
            sequence_occurrences = defaultdict(list)
            
            # Count sequence occurrences
            for i, seq in enumerate(sequences):
                seq_key = tuple(tuple(sorted(issues)) for issues in seq)
                sequence_counts[seq_key] += 1
                sequence_occurrences[seq_key].append(i)
            
            # Find repeating sequences
            for seq_key, count in sequence_counts.items():
                if count >= self.min_sequence_occurrences:
                    # Get timestamps for sequence occurrences
                    start_indices = sequence_occurrences[seq_key]
                    timestamps = []
                    for idx in start_indices:
                        for j in range(seq_len):
                            if idx + j < len(sorted_results):
                                timestamps.append(sorted_results[idx + j].timestamp)
                    
                    # Calculate temporal density
                    time_span = (max(timestamps) - min(timestamps)).total_seconds()
                    temporal_density = count / (time_span / 3600) if time_span > 0 else 0
                    
                    pattern = Pattern(
                        pattern_type="temporal",
                        description=f"Repeating sequence: {' -> '.join(str(list(issues)) for issues in seq_key)}",
                        significance=self._calculate_temporal_significance(
                            count,
                            seq_len,
                            temporal_density,
                            len(validation_results)
                        ),
                        occurrences=count,
                        first_seen=min(timestamps),
                        last_seen=max(timestamps),
                        related_issues=[issue for issues in seq_key for issue in issues],
                        metadata={
                            "sequence_length": seq_len,
                            "temporal_density": temporal_density
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _extract_sequences(
        self,
        results: List[ValidationResult],
        sequence_length: int
    ) -> List[List[List[str]]]:
        """Extract all possible sequences of given length"""
        sequences = []
        for i in range(len(results) - sequence_length + 1):
            sequence = []
            for j in range(sequence_length):
                sequence.append(results[i + j].issues)
            sequences.append(sequence)
        return sequences
    
    def _sequences_match(self, seq1: List[List[str]], seq2: List[List[str]]) -> bool:
        """Check if two sequences match (ignoring order within each step)"""
        if len(seq1) != len(seq2):
            return False
        return all(sorted(s1) == sorted(s2) for s1, s2 in zip(seq1, seq2))
    
    def _calculate_semantic_significance(
        self,
        cluster_size: int,
        avg_similarity: float,
        total_results: int
    ) -> float:
        """Calculate significance score for semantic patterns"""
        # Consider both cluster size and similarity
        size_factor = min(cluster_size / total_results * 2, 1.0)
        return (size_factor + avg_similarity) / 2
    
    def _calculate_temporal_significance(
        self,
        occurrences: int,
        sequence_length: int,
        temporal_density: float,
        total_results: int
    ) -> float:
        """Calculate significance score for temporal patterns"""
        # Consider sequence length, frequency, and temporal density
        length_factor = min(sequence_length / self.min_sequence_length, 1.0)
        occurrence_factor = min(occurrences / self.min_sequence_occurrences, 1.0)
        density_factor = min(temporal_density / 24, 1.0)  # Normalize to daily rate
        
        return (length_factor + occurrence_factor + density_factor) / 3 