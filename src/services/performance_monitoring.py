from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from collections import defaultdict
import statistics

from src.models.validation_result import ValidationResult
from src.services.pattern_recognition import Pattern
from src.services.recovery_management import RecoveryAction

class MetricType(Enum):
    """Types of performance metrics"""
    VALIDATION_SUCCESS_RATE = "validation_success_rate"
    RECOVERY_SUCCESS_RATE = "recovery_success_rate"
    PATTERN_DETECTION_RATE = "pattern_detection_rate"
    AVERAGE_CONFIDENCE_SCORE = "average_confidence_score"
    CRITICAL_FAILURE_RATE = "critical_failure_rate"
    RECOVERY_TIME = "recovery_time"

@dataclass
class PerformanceMetric:
    """Represents a performance metric measurement"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    window_size: timedelta
    metadata: Dict[str, Any]

class PerformanceMonitoringService:
    """Service for monitoring system performance metrics"""
    
    def __init__(self):
        """Initialize performance monitoring"""
        self.metrics_history: Dict[MetricType, List[PerformanceMetric]] = defaultdict(list)
        self.alert_thresholds: Dict[MetricType, float] = {
            MetricType.VALIDATION_SUCCESS_RATE: 0.8,
            MetricType.RECOVERY_SUCCESS_RATE: 0.7,
            MetricType.PATTERN_DETECTION_RATE: 0.6,
            MetricType.AVERAGE_CONFIDENCE_SCORE: 0.75,
            MetricType.CRITICAL_FAILURE_RATE: 0.2,
            MetricType.RECOVERY_TIME: 300  # seconds
        }
    
    def calculate_metrics(
        self,
        validation_results: List[ValidationResult],
        detected_patterns: List[Pattern],
        recovery_actions: List[Dict[str, Any]],
        window_size: timedelta = timedelta(hours=24)
    ) -> Dict[MetricType, PerformanceMetric]:
        """Calculate performance metrics for the given window"""
        current_time = datetime.now()
        window_start = current_time - window_size
        
        # Filter data within window
        recent_validations = [
            r for r in validation_results
            if r.timestamp >= window_start
        ]
        recent_patterns = [
            p for p in detected_patterns
            if p.last_seen >= window_start
        ]
        recent_recoveries = [
            r for r in recovery_actions
            if r["start_time"] >= window_start
        ]
        
        metrics = {}
        
        # Calculate validation success rate
        if recent_validations:
            success_rate = len([r for r in recent_validations if r.is_valid]) / len(recent_validations)
            metrics[MetricType.VALIDATION_SUCCESS_RATE] = PerformanceMetric(
                metric_type=MetricType.VALIDATION_SUCCESS_RATE,
                value=success_rate,
                timestamp=current_time,
                window_size=window_size,
                metadata={
                    "total_validations": len(recent_validations),
                    "successful_validations": len([r for r in recent_validations if r.is_valid])
                }
            )
        
        # Calculate recovery success rate
        if recent_recoveries:
            success_rate = len([r for r in recent_recoveries if r["status"] == "completed"]) / len(recent_recoveries)
            metrics[MetricType.RECOVERY_SUCCESS_RATE] = PerformanceMetric(
                metric_type=MetricType.RECOVERY_SUCCESS_RATE,
                value=success_rate,
                timestamp=current_time,
                window_size=window_size,
                metadata={
                    "total_recoveries": len(recent_recoveries),
                    "successful_recoveries": len([r for r in recent_recoveries if r["status"] == "completed"])
                }
            )
        
        # Calculate pattern detection rate
        if recent_validations and recent_patterns:
            detection_rate = len(recent_patterns) / len(recent_validations)
            metrics[MetricType.PATTERN_DETECTION_RATE] = PerformanceMetric(
                metric_type=MetricType.PATTERN_DETECTION_RATE,
                value=detection_rate,
                timestamp=current_time,
                window_size=window_size,
                metadata={
                    "total_validations": len(recent_validations),
                    "detected_patterns": len(recent_patterns)
                }
            )
        
        # Calculate average confidence score
        if recent_validations:
            avg_confidence = statistics.mean(r.confidence_score for r in recent_validations)
            metrics[MetricType.AVERAGE_CONFIDENCE_SCORE] = PerformanceMetric(
                metric_type=MetricType.AVERAGE_CONFIDENCE_SCORE,
                value=avg_confidence,
                timestamp=current_time,
                window_size=window_size,
                metadata={
                    "total_validations": len(recent_validations),
                    "score_distribution": self._calculate_score_distribution(recent_validations)
                }
            )
        
        # Calculate critical failure rate
        if recent_validations:
            critical_failures = [
                r for r in recent_validations
                if not r.is_valid and r.confidence_score >= 0.8
            ]
            critical_rate = len(critical_failures) / len(recent_validations)
            metrics[MetricType.CRITICAL_FAILURE_RATE] = PerformanceMetric(
                metric_type=MetricType.CRITICAL_FAILURE_RATE,
                value=critical_rate,
                timestamp=current_time,
                window_size=window_size,
                metadata={
                    "total_validations": len(recent_validations),
                    "critical_failures": len(critical_failures)
                }
            )
        
        # Calculate average recovery time
        if recent_recoveries:
            completed_recoveries = [
                r for r in recent_recoveries
                if r["status"] == "completed" and "end_time" in r
            ]
            if completed_recoveries:
                avg_time = statistics.mean(
                    (r["end_time"] - r["start_time"]).total_seconds()
                    for r in completed_recoveries
                )
                metrics[MetricType.RECOVERY_TIME] = PerformanceMetric(
                    metric_type=MetricType.RECOVERY_TIME,
                    value=avg_time,
                    timestamp=current_time,
                    window_size=window_size,
                    metadata={
                        "total_recoveries": len(recent_recoveries),
                        "completed_recoveries": len(completed_recoveries),
                        "time_distribution": self._calculate_time_distribution(completed_recoveries)
                    }
                )
        
        # Store metrics in history
        for metric in metrics.values():
            self.metrics_history[metric.metric_type].append(metric)
        
        return metrics
    
    def get_metric_history(
        self,
        metric_type: MetricType,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[PerformanceMetric]:
        """Get historical metrics for a specific type"""
        metrics = self.metrics_history.get(metric_type, [])
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        return sorted(metrics, key=lambda m: m.timestamp)
    
    def check_alerts(
        self,
        metrics: Dict[MetricType, PerformanceMetric]
    ) -> List[Dict[str, Any]]:
        """Check for metrics that exceed alert thresholds"""
        alerts = []
        
        for metric_type, threshold in self.alert_thresholds.items():
            if metric_type not in metrics:
                continue
                
            metric = metrics[metric_type]
            if self._should_alert(metric_type, metric.value, threshold):
                alerts.append({
                    "metric_type": metric_type,
                    "current_value": metric.value,
                    "threshold": threshold,
                    "timestamp": metric.timestamp,
                    "metadata": metric.metadata
                })
        
        return alerts
    
    def _should_alert(
        self,
        metric_type: MetricType,
        value: float,
        threshold: float
    ) -> bool:
        """Determine if a metric should trigger an alert"""
        if metric_type in [
            MetricType.VALIDATION_SUCCESS_RATE,
            MetricType.RECOVERY_SUCCESS_RATE,
            MetricType.PATTERN_DETECTION_RATE,
            MetricType.AVERAGE_CONFIDENCE_SCORE
        ]:
            return value < threshold
        else:
            return value > threshold
    
    def _calculate_score_distribution(
        self,
        validation_results: List[ValidationResult]
    ) -> Dict[str, int]:
        """Calculate distribution of confidence scores"""
        distribution = defaultdict(int)
        for result in validation_results:
            bucket = round(result.confidence_score * 10) / 10  # Round to nearest 0.1
            distribution[str(bucket)] += 1
        return dict(distribution)
    
    def _calculate_time_distribution(
        self,
        recovery_actions: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of recovery times"""
        distribution = defaultdict(int)
        for action in recovery_actions:
            duration = (action["end_time"] - action["start_time"]).total_seconds()
            bucket = f"{int(duration // 60)}m"  # Group by minute
            distribution[bucket] += 1
        return dict(distribution) 