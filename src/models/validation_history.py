from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from statistics import mean, stdev
import json
import os
from pathlib import Path
from .validation_result import ValidationResult

class ValidationHistory:
    """Tracks and analyzes validation results over time"""
    
    def __init__(self, storage_path: Optional[str] = None, max_age_days: int = 30, max_entries: int = 1000):
        """Initialize validation history
        
        Args:
            storage_path: Path to store history data. If None, no persistence is used.
            max_age_days: Maximum age of entries in days before they're archived
            max_entries: Maximum number of entries to keep in active history
        """
        self.history: List[ValidationResult] = []
        self.storage_path = storage_path
        self.max_age = timedelta(days=max_age_days)
        self.max_entries = max_entries
        if storage_path:
            self._load_history()
            
    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result to history"""
        self.history.append(result)
        self._rotate_history()
        if self.storage_path:
            self._save_history()
            
    def _rotate_history(self) -> None:
        """Rotate old entries to archive and maintain size limits"""
        if not self.history:
            return
            
        current_time = datetime.now()
        
        # Split history into active and archived based on age
        active_entries = []
        archived_entries = []
        
        for entry in self.history:
            if (current_time - entry.timestamp) <= self.max_age:
                active_entries.append(entry)
            else:
                archived_entries.append(entry)
                
        # If we still have too many entries, keep the most recent ones
        if len(active_entries) > self.max_entries:
            archived_entries.extend(active_entries[:-self.max_entries])
            active_entries = active_entries[-self.max_entries:]
            
        # Update active history
        self.history = active_entries
        
        # Archive old entries if we have storage
        if archived_entries and self.storage_path:
            self._archive_entries(archived_entries)
            
    def _archive_entries(self, entries: List[ValidationResult]) -> None:
        """Archive old entries to a separate file"""
        if not self.storage_path:
            return
            
        archive_path = self._get_archive_path()
        
        # Load existing archive if it exists
        archived_data = []
        if os.path.exists(archive_path):
            try:
                with open(archive_path, 'r') as f:
                    archived_data = json.load(f)
            except:
                archived_data = []
                
        # Add new entries to archive
        archived_data.extend([
            {
                "is_valid": e.is_valid,
                "issues": e.issues,
                "confidence_score": e.confidence_score,
                "timestamp": e.timestamp.isoformat()
            }
            for e in entries
        ])
        
        # Save updated archive
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        with open(archive_path, 'w') as f:
            json.dump(archived_data, f, indent=2)
            
    def _get_archive_path(self) -> str:
        """Get the path for the archive file"""
        if not self.storage_path:
            return ""
        
        base_path = Path(self.storage_path)
        return str(base_path.parent / f"{base_path.stem}_archive{base_path.suffix}")
        
    def clear_history(self, include_archive: bool = False) -> None:
        """Clear validation history
        
        Args:
            include_archive: If True, also clear archived data
        """
        self.history = []
        if self.storage_path and os.path.exists(self.storage_path):
            os.remove(self.storage_path)
            
        if include_archive:
            archive_path = self._get_archive_path()
            if os.path.exists(archive_path):
                os.remove(archive_path)
                
    def _save_history(self) -> None:
        """Save validation history to storage"""
        if not self.storage_path:
            return
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Convert history to serializable format
        history_data = [
            {
                "is_valid": r.is_valid,
                "issues": r.issues,
                "confidence_score": r.confidence_score,
                "timestamp": r.timestamp.isoformat()
            }
            for r in self.history
        ]
        
        # Save to file
        with open(self.storage_path, 'w') as f:
            json.dump(history_data, f, indent=2)
            
    def _load_history(self) -> None:
        """Load validation history from storage"""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
            
        try:
            with open(self.storage_path, 'r') as f:
                history_data = json.load(f)
                
            # Convert data back to ValidationResult objects
            self.history = [
                ValidationResult(
                    is_valid=r["is_valid"],
                    issues=r["issues"],
                    confidence_score=r["confidence_score"],
                    timestamp=datetime.fromisoformat(r["timestamp"])
                )
                for r in history_data
            ]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If there's an error loading the history, start fresh
            self.history = []
            
    def get_average_confidence(self, time_window: Optional[timedelta] = None) -> float:
        """Get average confidence score, optionally within a time window"""
        if not self.history:
            return 0.0
            
        if time_window is None:
            scores = [r.confidence_score for r in self.history]
        else:
            cutoff = datetime.now() - time_window
            scores = [r.confidence_score for r in self.history if r.timestamp >= cutoff]
            
        return sum(scores) / max(len(scores), 1)
    
    def get_common_issues(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most common validation issues with their frequencies"""
        issue_counts: Dict[str, int] = {}
        for result in self.history:
            for issue in result.issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
                
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_issues[:limit]
        
    def get_issue_categories(self) -> Dict[str, Dict[str, int]]:
        """Categorize issues into predefined categories and count occurrences"""
        categories = {
            "technical_level": 0,
            "content_coverage": 0,
            "system_errors": 0,
            "improvement_suggestions": 0
        }
        
        for result in self.history:
            for issue in result.issues:
                issue_lower = issue.lower()
                if "technical level" in issue_lower:
                    categories["technical_level"] += 1
                elif any(term in issue_lower for term in ["coverage", "criterion", "missing", "incomplete"]):
                    categories["content_coverage"] += 1
                elif any(term in issue_lower for term in ["error", "timeout", "failed"]):
                    categories["system_errors"] += 1
                else:
                    categories["improvement_suggestions"] += 1
                    
        return {
            "categories": categories,
            "total_validations": len(self.history),
            "failed_validations": sum(1 for r in self.history if not r.is_valid)
        }
        
    def get_trend_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get a comprehensive summary of validation trends"""
        categories = self.get_issue_categories()
        avg_confidence = self.get_average_confidence(time_window)
        common_issues = self.get_common_issues()
        
        total = categories["total_validations"]
        if total == 0:
            return {
                "average_confidence": 0.0,
                "failure_rate": 0.0,
                "categories": categories["categories"],
                "common_issues": common_issues
            }
            
        return {
            "average_confidence": avg_confidence,
            "failure_rate": categories["failed_validations"] / total,
            "categories": categories["categories"],
            "common_issues": common_issues
        } 
        
    def get_time_series_analysis(self, period: timedelta = timedelta(days=1)) -> List[Dict[str, Any]]:
        """Analyze validation trends over time periods
        
        Args:
            period: Time period for each bucket (default: 1 day)
            
        Returns:
            List of trend data points, each containing:
            - timestamp: Start of the period
            - validation_count: Number of validations
            - failure_rate: Rate of failed validations
            - confidence_avg: Average confidence score
            - categories: Issue category counts
        """
        if not self.history:
            return []
            
        # Find time range
        start_time = min(r.timestamp for r in self.history)
        end_time = max(r.timestamp for r in self.history)
        
        # Create time buckets
        current = start_time
        time_series = []
        
        while current <= end_time:
            period_end = current + period
            
            # Filter results in this period
            period_results = [
                r for r in self.history 
                if current <= r.timestamp < period_end
            ]
            
            if period_results:
                # Calculate metrics for this period
                categories = {
                    "technical_level": 0,
                    "content_coverage": 0,
                    "system_errors": 0,
                    "improvement_suggestions": 0
                }
                
                for result in period_results:
                    for issue in result.issues:
                        issue_lower = issue.lower()
                        if "technical level" in issue_lower:
                            categories["technical_level"] += 1
                        elif any(term in issue_lower for term in ["coverage", "criterion", "missing", "incomplete"]):
                            categories["content_coverage"] += 1
                        elif any(term in issue_lower for term in ["error", "timeout", "failed"]):
                            categories["system_errors"] += 1
                        else:
                            categories["improvement_suggestions"] += 1
                
                time_series.append({
                    "timestamp": current,
                    "validation_count": len(period_results),
                    "failure_rate": sum(1 for r in period_results if not r.is_valid) / len(period_results),
                    "confidence_avg": sum(r.confidence_score for r in period_results) / len(period_results),
                    "categories": categories
                })
            
            current = period_end
            
        return time_series 
        
    def detect_trends(self, window_size: int = 5, threshold: float = 2.0) -> Dict[str, Any]:
        """Detect significant trends in validation metrics
        
        Args:
            window_size: Number of recent validations to compare against history
            threshold: Number of standard deviations to consider significant
            
        Returns:
            Dictionary containing detected trends:
            - confidence_trend: Direction and significance of confidence change
            - failure_trend: Direction and significance of failure rate change
            - issue_trends: Significant changes in issue categories
            - alerts: List of significant changes that may need attention
        """
        if len(self.history) < window_size * 2:
            return {
                "confidence_trend": "insufficient_data",
                "failure_trend": "insufficient_data",
                "issue_trends": {},
                "alerts": []
            }
            
        # Split into recent and historical windows
        recent = self.history[-window_size:]
        historical = self.history[:-window_size]
        
        alerts = []
        
        # Analyze confidence scores
        recent_confidence = [r.confidence_score for r in recent]
        historical_confidence = [r.confidence_score for r in historical]
        
        confidence_trend = self._analyze_metric_trend(
            recent_confidence,
            historical_confidence,
            threshold,
            "confidence score"
        )
        
        # Analyze failure rates
        recent_failures = [0 if r.is_valid else 1 for r in recent]
        historical_failures = [0 if r.is_valid else 1 for r in historical]
        
        failure_trend = self._analyze_metric_trend(
            recent_failures,
            historical_failures,
            threshold,
            "failure rate"
        )
        
        # Analyze issue categories
        issue_trends = {}
        for category in ["technical_level", "content_coverage", "system_errors", "improvement_suggestions"]:
            recent_issues = self._count_category_issues(recent, category)
            historical_issues = self._count_category_issues(historical, category)
            
            trend = self._analyze_metric_trend(
                recent_issues,
                historical_issues,
                threshold,
                f"{category} issues"
            )
            
            issue_trends[category] = trend["trend"]
            if trend["alert"]:
                alerts.append(trend["alert"])
                
        # Add overall trends to alerts if significant
        if confidence_trend["alert"]:
            alerts.append(confidence_trend["alert"])
        if failure_trend["alert"]:
            alerts.append(failure_trend["alert"])
            
        return {
            "confidence_trend": confidence_trend["trend"],
            "failure_trend": failure_trend["trend"],
            "issue_trends": issue_trends,
            "alerts": alerts
        }
        
    def _analyze_metric_trend(
        self,
        recent: List[float],
        historical: List[float],
        threshold: float,
        metric_name: str
    ) -> Dict[str, Any]:
        """Analyze trend in a metric by comparing recent vs historical values"""
        if not recent or not historical:
            return {"trend": "no_change", "alert": None}
            
        recent_avg = mean(recent)
        historical_avg = mean(historical)
        
        try:
            # Calculate pooled standard deviation for more stable comparison
            n1, n2 = len(recent), len(historical)
            if n1 < 2 or n2 < 2:  # Need at least 2 points for std
                return {"trend": "no_change", "alert": None}
                
            s1 = stdev(recent)
            s2 = stdev(historical)
            
            # Add small epsilon to avoid division by zero and make detection more conservative
            epsilon = 0.001
            pooled_std = ((n1-1)*s1*s1 + (n2-1)*s2*s2)/(n1+n2-2) + epsilon
            
            # Calculate effect size (Cohen's d) with correction for small samples
            # Hedges' g correction factor
            correction = (1 - 3/(4*(n1 + n2) - 9))
            effect_size = abs(recent_avg - historical_avg) / (pooled_std ** 0.5) * correction
                
        except:
            return {"trend": "no_change", "alert": None}
            
        if effect_size < threshold:
            return {"trend": "no_change", "alert": None}
            
        if recent_avg > historical_avg:
            trend = "increasing"
            alert = f"Significant increase in {metric_name} (effect={effect_size:.2f})"
        else:
            trend = "decreasing"
            alert = f"Significant decrease in {metric_name} (effect={effect_size:.2f})"
            
        return {"trend": trend, "alert": alert}
        
    def _count_category_issues(self, results: List[ValidationResult], category: str) -> List[float]:
        """Count issues in a category for each validation result"""
        counts = []
        for result in results:
            category_count = 0
            for issue in result.issues:
                issue_lower = issue.lower()
                if category == "technical_level" and "technical level" in issue_lower:
                    category_count += 1
                elif category == "content_coverage" and any(term in issue_lower for term in ["coverage", "criterion", "missing", "incomplete"]):
                    category_count += 1
                elif category == "system_errors" and any(term in issue_lower for term in ["error", "timeout", "failed"]):
                    category_count += 1
                elif category == "improvement_suggestions" and not any(term in issue_lower for term in ["technical level", "coverage", "criterion", "missing", "incomplete", "error", "timeout", "failed"]):
                    category_count += 1
            counts.append(float(category_count))
        return counts 
        
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on validation history and trends
        
        Returns:
            List of recommendations, each containing:
            - category: Type of recommendation (quality, technical, system, content)
            - priority: Priority level (high, medium, low)
            - issue: The issue being addressed
            - recommendation: Specific action to take
            - evidence: Supporting data for the recommendation
        """
        if len(self.history) < 5:  # Need some history for meaningful recommendations
            return []
            
        recommendations = []
        trends = self.detect_trends(window_size=5)
        recent_summary = self.get_trend_summary(timedelta(days=1))
        
        # Check for declining confidence
        if trends["confidence_trend"] == "decreasing":
            recommendations.append({
                "category": "quality",
                "priority": "high",
                "issue": "Declining validation confidence",
                "recommendation": "Review recent content changes and validation criteria",
                "evidence": f"Confidence score has significantly decreased (current: {recent_summary['average_confidence']:.2f})"
            })
            
        # Check for increasing failure rate
        if trends["failure_trend"] == "increasing":
            recommendations.append({
                "category": "quality",
                "priority": "high",
                "issue": "Increasing validation failures",
                "recommendation": "Audit recent content additions and review validation standards",
                "evidence": f"Failure rate has increased to {recent_summary['failure_rate']:.1%}"
            })
            
        # Check for recurring technical level issues
        tech_level_count = recent_summary["categories"]["technical_level"]
        if tech_level_count > 0 and trends["issue_trends"].get("technical_level") == "increasing":
            recommendations.append({
                "category": "technical",
                "priority": "medium",
                "issue": "Recurring technical level mismatches",
                "recommendation": "Review technical level criteria and content complexity guidelines",
                "evidence": f"Found {tech_level_count} technical level issues in recent validations"
            })
            
        # Check for content coverage issues
        coverage_count = recent_summary["categories"]["content_coverage"]
        if coverage_count > 0:
            recommendations.append({
                "category": "content",
                "priority": "medium" if coverage_count > 2 else "low",
                "issue": "Incomplete content coverage",
                "recommendation": "Add missing examples and expand content coverage",
                "evidence": f"Found {coverage_count} content coverage issues"
            })
            
        # Check for system errors
        error_count = recent_summary["categories"]["system_errors"]
        if error_count > 0:  # Changed condition to trigger on any system errors
            recommendations.append({
                "category": "system",
                "priority": "high",
                "issue": "System errors detected",
                "recommendation": "Review system logs and validation timeouts",
                "evidence": f"Found {error_count} system errors in recent validations"
            })
            
        # Sort recommendations by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order[x["priority"]])
        
        return recommendations 
        
    def analyze_archive(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Analyze both active and archived validation data for long-term patterns
        
        Args:
            time_window: Optional time window to limit analysis (None for all time)
            
        Returns:
            Dictionary containing:
            - total_validations: Total number of validations
            - historical_confidence: Average confidence over time periods
            - recurring_issues: Issues that appear repeatedly
            - stability_metrics: System stability indicators
            - improvement_indicators: Metrics showing improvement or degradation
        """
        if not self.storage_path:
            return self._analyze_data(self.history, time_window)
            
        # Load archived data
        archive_path = self._get_archive_path()
        archived_results = []
        
        if os.path.exists(archive_path):
            try:
                with open(archive_path, 'r') as f:
                    archived_data = json.load(f)
                    
                archived_results = [
                    ValidationResult(
                        is_valid=r["is_valid"],
                        issues=r["issues"],
                        confidence_score=r["confidence_score"],
                        timestamp=datetime.fromisoformat(r["timestamp"])
                    )
                    for r in archived_data
                ]
            except:
                archived_results = []
                
        # Combine active and archived data
        all_results = archived_results + self.history
        
        return self._analyze_data(all_results, time_window)
        
    def _analyze_data(self, results: List[ValidationResult], time_window: Optional[timedelta]) -> Dict[str, Any]:
        """Analyze a set of validation results"""
        if not results:
            return {
                "total_validations": 0,
                "historical_confidence": [],
                "recurring_issues": [],
                "stability_metrics": {
                    "error_rate": 0.0,
                    "average_confidence": 0.0,
                    "consistency_score": 0.0
                },
                "improvement_indicators": {
                    "trend": "insufficient_data",
                    "confidence_change": 0.0,
                    "error_rate_change": 0.0
                }
            }
            
        # Filter by time window if specified
        if time_window:
            cutoff = datetime.now() - time_window
            results = [r for r in results if r.timestamp >= cutoff]
            
        if not results:
            return self._analyze_data([], None)  # Return empty analysis
            
        # Sort results by timestamp
        results.sort(key=lambda x: x.timestamp)
        
        # Calculate historical confidence over time
        period = timedelta(days=7)  # Weekly periods
        historical_confidence = []
        current_time = results[0].timestamp
        end_time = results[-1].timestamp
        
        while current_time <= end_time:
            period_end = current_time + period
            period_results = [r for r in results if current_time <= r.timestamp < period_end]
            
            if period_results:
                avg_confidence = sum(r.confidence_score for r in period_results) / len(period_results)
                historical_confidence.append({
                    "period_start": current_time.isoformat(),
                    "average_confidence": avg_confidence,
                    "validation_count": len(period_results)
                })
                
            current_time = period_end
            
        # Analyze recurring issues
        issue_occurrences = {}
        for result in results:
            for issue in result.issues:
                if issue not in issue_occurrences:
                    issue_occurrences[issue] = {
                        "count": 0,
                        "first_seen": result.timestamp,
                        "last_seen": result.timestamp
                    }
                occurrence = issue_occurrences[issue]
                occurrence["count"] += 1
                occurrence["last_seen"] = max(occurrence["last_seen"], result.timestamp)
                
        recurring_issues = [
            {
                "issue": issue,
                "count": data["count"],
                "first_seen": data["first_seen"].isoformat(),
                "last_seen": data["last_seen"].isoformat(),
                "frequency": data["count"] / len(results)
            }
            for issue, data in issue_occurrences.items()
            if data["count"] > 1  # Only include truly recurring issues
        ]
        recurring_issues.sort(key=lambda x: x["count"], reverse=True)
        
        # Calculate stability metrics
        error_rate = sum(1 for r in results if not r.is_valid) / len(results)
        avg_confidence = sum(r.confidence_score for r in results) / len(results)
        
        # Calculate consistency score (lower variance is better)
        confidence_values = [r.confidence_score for r in results]
        try:
            confidence_std = stdev(confidence_values)
            consistency_score = 1.0 - min(confidence_std, 1.0)  # Higher is better
        except:
            consistency_score = 1.0
            
        # Calculate improvement indicators
        if len(results) >= 10:
            recent = results[-5:]
            historical = results[:-5]
            
            recent_confidence = sum(r.confidence_score for r in recent) / len(recent)
            historical_confidence = sum(r.confidence_score for r in historical) / len(historical)
            confidence_change = recent_confidence - historical_confidence
            
            recent_error_rate = sum(1 for r in recent if not r.is_valid) / len(recent)
            historical_error_rate = sum(1 for r in historical if not r.is_valid) / len(historical)
            error_rate_change = recent_error_rate - historical_error_rate
            
            if confidence_change > 0.1 and error_rate_change < -0.1:
                trend = "improving"
            elif confidence_change < -0.1 and error_rate_change > 0.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
            confidence_change = 0.0
            error_rate_change = 0.0
            
        return {
            "total_validations": len(results),
            "historical_confidence": historical_confidence,
            "recurring_issues": recurring_issues,
            "stability_metrics": {
                "error_rate": error_rate,
                "average_confidence": avg_confidence,
                "consistency_score": consistency_score
            },
            "improvement_indicators": {
                "trend": trend,
                "confidence_change": confidence_change,
                "error_rate_change": error_rate_change
            }
        } 
        
    def get_validation_patterns(self, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """Identify recurring patterns in validation results
        
        Args:
            min_occurrences: Minimum number of occurrences to consider a pattern
            
        Returns:
            List of patterns, each containing:
            - pattern_type: Type of pattern (issue_sequence, confidence_pattern, timing_pattern)
            - description: Human-readable description of the pattern
            - occurrences: Number of times the pattern occurred
            - examples: List of validation results exhibiting the pattern
            - significance: Score indicating pattern significance (0-1)
        """
        if len(self.history) < min_occurrences:
            return []
        
        patterns = []
        
        # Look for issue sequence patterns
        issue_patterns = self._find_issue_sequences(min_occurrences)
        patterns.extend(issue_patterns)
        
        # Look for confidence score patterns
        confidence_patterns = self._find_confidence_patterns(min_occurrences)
        patterns.extend(confidence_patterns)
        
        # Look for timing patterns
        timing_patterns = self._find_timing_patterns(min_occurrences)
        patterns.extend(timing_patterns)
        
        # Sort by significance
        patterns.sort(key=lambda x: x["significance"], reverse=True)
        return patterns

    def _find_issue_sequences(self, min_occurrences: int) -> List[Dict[str, Any]]:
        """Find recurring sequences of validation issues"""
        sequences = {}
        
        # Look for sequences of 2-3 validation results
        for seq_length in range(2, 4):
            if len(self.history) < seq_length:
                continue
            
            for i in range(len(self.history) - seq_length + 1):
                sequence = self.history[i:i + seq_length]
                
                # Create pattern key from issues and validity
                pattern_key = tuple(
                    (r.is_valid, tuple(sorted(r.issues)))
                    for r in sequence
                )
                
                if pattern_key not in sequences:
                    sequences[pattern_key] = {
                        "count": 0,
                        "examples": []
                    }
                    
                sequences[pattern_key]["count"] += 1
                if len(sequences[pattern_key]["examples"]) < 3:  # Keep up to 3 examples
                    sequences[pattern_key]["examples"].append(sequence)
                    
        # Convert to pattern format
        patterns = []
        for pattern_key, data in sequences.items():
            if data["count"] >= min_occurrences:
                # Calculate significance based on sequence length and frequency
                significance = min(
                    (len(pattern_key) * data["count"]) / len(self.history),
                    1.0
                )
                
                # Create human-readable description
                steps = []
                for is_valid, issues in pattern_key:
                    status = "valid" if is_valid else "invalid"
                    if issues:
                        status += f" with issues: {', '.join(issues)}"
                    steps.append(status)
                    
                patterns.append({
                    "pattern_type": "issue_sequence",
                    "description": f"Sequence: {' → '.join(steps)}",
                    "occurrences": data["count"],
                    "examples": data["examples"],
                    "significance": significance
                })
                
        return patterns

    def _find_confidence_patterns(self, min_occurrences: int) -> List[Dict[str, Any]]:
        """Find patterns in confidence score changes"""
        if len(self.history) < 3:  # Need at least 3 points for trend
            return []
        
        patterns = []
        
        # Look for consistent confidence changes
        confidence_changes = []
        for i in range(1, len(self.history)):
            prev = self.history[i-1].confidence_score
            curr = self.history[i].confidence_score
            confidence_changes.append(curr - prev)
            
        # Check for consistent decline/improvement
        avg_change = sum(confidence_changes) / len(confidence_changes)
        if abs(avg_change) >= 0.1:  # Significant average change
            consistent_direction = all(
                (c > 0 and avg_change > 0) or (c < 0 and avg_change < 0)
                for c in confidence_changes
            )
            
            if consistent_direction:
                direction = "improving" if avg_change > 0 else "declining"
                patterns.append({
                    "pattern_type": "confidence_pattern",
                    "description": f"Consistently {direction} confidence scores",
                    "occurrences": len(confidence_changes),
                    "examples": self.history[-3:],  # Last 3 examples
                    "significance": min(abs(avg_change) * 2, 1.0)
                })
                
        return patterns

    def _find_timing_patterns(self, min_occurrences: int) -> List[Dict[str, Any]]:
        """Find patterns in validation timing"""
        if len(self.history) < min_occurrences:
            return []
        
        patterns = []
        
        # Calculate time deltas between validations
        time_deltas = []
        for i in range(1, len(self.history)):
            delta = self.history[i].timestamp - self.history[i-1].timestamp
            time_deltas.append(delta.total_seconds())
            
        # Look for regular intervals
        if len(time_deltas) >= 3:
            avg_delta = sum(time_deltas) / len(time_deltas)
            variance = sum((d - avg_delta) ** 2 for d in time_deltas) / len(time_deltas)
            
            if variance < avg_delta * 0.25:  # Low variance indicates regular interval
                interval_str = self._format_time_interval(avg_delta)
                patterns.append({
                    "pattern_type": "timing_pattern",
                    "description": f"Regular validation interval of {interval_str}",
                    "occurrences": len(time_deltas),
                    "examples": self.history[-3:],  # Last 3 examples
                    "significance": 1.0 - (variance / (avg_delta * avg_delta))
                })
                
        return patterns

    def _format_time_interval(self, seconds: float) -> str:
        """Format a time interval in seconds to human-readable string"""
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.0f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        else:
            return f"{seconds/86400:.1f} days" 

    def find_related_issues(self, issue: str, min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """Find semantically related issues
        
        Args:
            issue: The issue to find relations for
            min_similarity: Minimum similarity score (0-1) to consider issues related
            
        Returns:
            List of related issues, each containing:
            - issue: The related issue text
            - similarity: Similarity score (0-1)
            - occurrences: Number of times this issue appeared
            - first_seen: Timestamp of first occurrence
            - last_seen: Timestamp of last occurrence
        """
        if not self.history:
            return []
        
        # Get all unique issues
        all_issues = {}
        for result in self.history:
            for result_issue in result.issues:
                if result_issue not in all_issues:
                    all_issues[result_issue] = {
                        "occurrences": 0,
                        "first_seen": result.timestamp,
                        "last_seen": result.timestamp
                    }
                occurrence = all_issues[result_issue]
                occurrence["occurrences"] += 1
                occurrence["first_seen"] = min(occurrence["first_seen"], result.timestamp)
                occurrence["last_seen"] = max(occurrence["last_seen"], result.timestamp)
        
        # Calculate semantic similarity
        related = []
        issue_lower = issue.lower()
        issue_words = set(issue_lower.split())
        
        # Define key phrases that should be treated as units
        key_phrases = [
            "technical level",
            "code examples",
            "missing examples",
            "examples needed",
            "system error",
            "runtime error",
            "error in processing"
        ]
        
        for other_issue, occurrence in all_issues.items():
            if other_issue == issue:
                continue
            
            other_lower = other_issue.lower()
            other_words = set(other_lower.split())
            
            # Calculate base similarity using Jaccard similarity
            intersection = len(issue_words & other_words)
            union = len(issue_words | other_words)
            base_similarity = intersection / max(union, 1)
            
            # Boost similarity for matching key phrases
            phrase_boost = 0.0
            for phrase in key_phrases:
                if phrase in issue_lower and phrase in other_lower:
                    phrase_boost += 0.3  # Significant boost for matching phrases
                elif (phrase in issue_lower and any(word in other_lower for word in phrase.split())) or \
                     (phrase in other_lower and any(word in issue_lower for word in phrase.split())):
                    phrase_boost += 0.15  # Partial phrase match
                    
            # Boost similarity for common key terms
            key_terms = {
                "technical", "level", "content", "missing", "error", 
                "invalid", "incomplete", "examples", "code", "needed",
                "advanced", "basic", "system", "runtime", "processing"
            }
            common_key_terms = len([w for w in issue_words & other_words if w in key_terms])
            key_term_boost = min(common_key_terms * 0.2, 0.4)  # Increased boost per term
            
            # Calculate final similarity with boosts
            similarity = min(base_similarity + phrase_boost + key_term_boost, 1.0)
            
            if similarity >= min_similarity:
                related.append({
                    "issue": other_issue,
                    "similarity": similarity,
                    "occurrences": occurrence["occurrences"],
                    "first_seen": occurrence["first_seen"].isoformat(),
                    "last_seen": occurrence["last_seen"].isoformat()
                })
        
        # Sort by similarity then occurrences
        related.sort(key=lambda x: (-x["similarity"], -x["occurrences"]))
        return related

    def get_issue_clusters(self, min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """Group semantically related issues into clusters
        
        Args:
            min_similarity: Minimum similarity score to consider issues related
            
        Returns:
            List of clusters, each containing:
            - issues: List of issues in the cluster
            - total_occurrences: Total occurrences of all issues in cluster
            - time_span: Time span between first and last occurrence
            - common_terms: Common terms shared by issues in cluster
        """
        if not self.history:
            return []
        
        # Get all unique issues
        all_issues = set()
        for result in self.history:
            all_issues.update(result.issues)
        
        # Build clusters
        clusters = []
        unclustered = set(all_issues)
        
        while unclustered:
            seed = unclustered.pop()
            cluster = {seed}
            
            # Find directly and transitively related issues until no more can be added
            cluster_size = 0
            while len(cluster) > cluster_size:
                cluster_size = len(cluster)
                
                # Find all issues related to any issue in the cluster
                related_issues = set()
                for cluster_issue in cluster:
                    related = self.find_related_issues(cluster_issue, min_similarity)
                    related_issues.update(item["issue"] for item in related)
                
                # Add related issues that are still unclustered
                cluster.update(related_issues & unclustered)
            
            # Remove clustered issues from unclustered set
            unclustered -= cluster
            
            if cluster:  # Only add non-empty clusters
                # Calculate cluster metrics
                occurrences = 0
                first_seen = None
                last_seen = None
                
                for result in self.history:
                    cluster_issues = set(result.issues) & cluster
                    if cluster_issues:
                        occurrences += len(cluster_issues)
                        if first_seen is None:
                            first_seen = result.timestamp
                        last_seen = result.timestamp
                
                # Find common terms
                common_terms = set.intersection(*[set(issue.lower().split()) for issue in cluster])
                
                clusters.append({
                    "issues": sorted(list(cluster)),
                    "total_occurrences": occurrences,
                    "time_span": (last_seen - first_seen).total_seconds() if first_seen else 0,
                    "common_terms": sorted(list(common_terms))
                })
        
        # Merge similar clusters
        i = 0
        while i < len(clusters):
            j = i + 1
            while j < len(clusters):
                # Check if clusters share any common terms
                common = set(clusters[i]["common_terms"]) & set(clusters[j]["common_terms"])
                if common and any(term not in {"in", "the", "and", "or", "with"} for term in common):
                    # Merge clusters
                    clusters[i]["issues"].extend(clusters[j]["issues"])
                    clusters[i]["issues"] = sorted(set(clusters[i]["issues"]))
                    clusters[i]["total_occurrences"] += clusters[j]["total_occurrences"]
                    clusters[i]["common_terms"] = sorted(common)
                    clusters.pop(j)
                else:
                    j += 1
            i += 1
        
        # Sort clusters by total occurrences
        clusters.sort(key=lambda x: x["total_occurrences"], reverse=True)
        return clusters 