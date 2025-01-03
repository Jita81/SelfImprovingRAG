import pytest
from datetime import datetime, timedelta
import numpy as np
from src.services.pattern_recognition import PatternRecognitionService, Pattern
from src.models.validation_result import ValidationResult

class MockEmbeddingModel:
    """Mock embedding model for testing"""
    def encode(self, texts):
        # Create simple mock embeddings that cluster similar texts
        embeddings = []
        for text in texts:
            if "technical" in text.lower():
                embeddings.append([1.0, 0.0, 0.0])
            elif "missing" in text.lower():
                embeddings.append([0.0, 1.0, 0.0])
            else:
                embeddings.append([0.0, 0.0, 1.0])
        return np.array(embeddings)

@pytest.fixture
def pattern_recognition():
    return PatternRecognitionService(MockEmbeddingModel())

@pytest.fixture
def sample_validation_results():
    base_time = datetime.now()
    return [
        ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch"],
            confidence_score=0.4,
            timestamp=base_time
        ),
        ValidationResult(
            is_valid=False,
            issues=["Technical level too advanced"],
            confidence_score=0.5,
            timestamp=base_time + timedelta(hours=1)
        ),
        ValidationResult(
            is_valid=False,
            issues=["Missing examples"],
            confidence_score=0.6,
            timestamp=base_time + timedelta(hours=2)
        ),
        ValidationResult(
            is_valid=False,
            issues=["Missing documentation"],
            confidence_score=0.4,
            timestamp=base_time + timedelta(hours=3)
        ),
        ValidationResult(
            is_valid=False,
            issues=["System error occurred"],
            confidence_score=0.3,
            timestamp=base_time + timedelta(hours=4)
        )
    ]

def test_empty_validation_history(pattern_recognition):
    """Test pattern recognition with empty history"""
    patterns = pattern_recognition.analyze_validation_history([])
    assert patterns == []

def test_semantic_pattern_detection(pattern_recognition, sample_validation_results):
    """Test detection of semantically similar issues"""
    patterns = pattern_recognition.analyze_validation_history(sample_validation_results)
    
    # Should find at least two clusters: technical issues and missing issues
    semantic_patterns = [p for p in patterns if p.pattern_type == "semantic"]
    assert len(semantic_patterns) >= 2
    
    # Check technical issues cluster
    tech_pattern = next(p for p in semantic_patterns 
                       if "technical" in p.description.lower())
    assert tech_pattern.occurrences >= 2
    assert any("technical level mismatch" in issue.lower() 
              for issue in tech_pattern.related_issues)
    assert any("technical level too advanced" in issue.lower() 
              for issue in tech_pattern.related_issues)
    assert tech_pattern.significance > 0.0
    
    # Check missing issues cluster
    missing_pattern = next(p for p in semantic_patterns 
                         if "missing" in p.description.lower())
    assert missing_pattern.occurrences >= 2
    assert any("missing examples" in issue.lower() 
              for issue in missing_pattern.related_issues)
    assert any("missing documentation" in issue.lower() 
              for issue in missing_pattern.related_issues)
    assert missing_pattern.significance > 0.0

def test_temporal_pattern_detection(pattern_recognition):
    """Test detection of temporal patterns"""
    # Create a repeating sequence
    base_time = datetime.now()
    sequence = [
        ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch"],
            confidence_score=0.4,
            timestamp=base_time
        ),
        ValidationResult(
            is_valid=False,
            issues=["Missing examples"],
            confidence_score=0.5,
            timestamp=base_time + timedelta(hours=1)
        )
    ]
    
    # Repeat sequence three times
    validation_results = []
    for i in range(3):
        for j, result in enumerate(sequence):
            validation_results.append(ValidationResult(
                is_valid=result.is_valid,
                issues=result.issues,
                confidence_score=result.confidence_score,
                timestamp=base_time + timedelta(hours=i*2 + j)
            ))
    
    patterns = pattern_recognition.analyze_validation_history(validation_results)
    temporal_patterns = [p for p in patterns if p.pattern_type == "temporal"]
    
    assert len(temporal_patterns) > 0
    pattern = temporal_patterns[0]
    assert pattern.occurrences >= 3
    assert "technical level mismatch" in pattern.description.lower()
    assert "missing examples" in pattern.description.lower()
    assert pattern.significance > 0.0

def test_significance_threshold(pattern_recognition, sample_validation_results):
    """Test filtering patterns by significance threshold"""
    # Test with different thresholds
    high_threshold = 0.8
    patterns_high = pattern_recognition.analyze_validation_history(
        sample_validation_results,
        min_significance=high_threshold
    )
    
    low_threshold = 0.2
    patterns_low = pattern_recognition.analyze_validation_history(
        sample_validation_results,
        min_significance=low_threshold
    )
    
    # Higher threshold should return fewer patterns
    assert len(patterns_high) <= len(patterns_low)
    
    # All patterns should meet their respective thresholds
    assert all(p.significance >= high_threshold for p in patterns_high)
    assert all(p.significance >= low_threshold for p in patterns_low)

def test_pattern_metadata(pattern_recognition, sample_validation_results):
    """Test pattern metadata completeness"""
    patterns = pattern_recognition.analyze_validation_history(sample_validation_results)
    
    for pattern in patterns:
        # Check required fields
        assert pattern.pattern_type in ["semantic", "temporal"]
        assert isinstance(pattern.description, str)
        assert 0.0 <= pattern.significance <= 1.0
        assert pattern.occurrences > 0
        assert isinstance(pattern.first_seen, datetime)
        assert isinstance(pattern.last_seen, datetime)
        assert pattern.first_seen <= pattern.last_seen
        assert len(pattern.related_issues) > 0
        
        # Check metadata
        assert isinstance(pattern.metadata, dict)
        if pattern.pattern_type == "semantic":
            assert "cluster_size" in pattern.metadata
            assert "average_similarity" in pattern.metadata
            assert 0.0 <= pattern.metadata["average_similarity"] <= 1.0
        elif pattern.pattern_type == "temporal":
            assert "sequence_length" in pattern.metadata
            assert "temporal_density" in pattern.metadata

def test_sequence_matching(pattern_recognition):
    """Test sequence matching logic"""
    seq1 = [["A", "B"], ["C", "D"]]
    seq2 = [["B", "A"], ["D", "C"]]  # Same content, different order
    assert pattern_recognition._sequences_match(seq1, seq2)
    
    seq3 = [["A", "B"], ["C"]]  # Different length
    assert not pattern_recognition._sequences_match(seq1, seq3)
    
    seq4 = [["A", "B"], ["C", "E"]]  # Different content
    assert not pattern_recognition._sequences_match(seq1, seq4) 