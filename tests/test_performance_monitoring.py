import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.services.performance_monitoring import (
    PerformanceMonitoringService,
    MetricType,
    PerformanceMetric
)
from src.models.validation_result import ValidationResult
from src.services.pattern_recognition import Pattern

@pytest.fixture
def monitoring_service():
    return PerformanceMonitoringService()

@pytest.fixture
def sample_validation_results():
    base_time = datetime.now()
    return [
        ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=base_time - timedelta(hours=1)
        ),
        ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch"],
            confidence_score=0.8,
            timestamp=base_time - timedelta(minutes=30)
        ),
        ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.85,
            timestamp=base_time
        )
    ]

@pytest.fixture
def sample_patterns():
    base_time = datetime.now()
    return [
        Pattern(
            pattern_type="semantic",
            description="Technical level issues",
            significance=0.8,
            occurrences=2,
            first_seen=base_time - timedelta(hours=2),
            last_seen=base_time - timedelta(hours=1),
            related_issues=["Technical level mismatch"],
            metadata={"cluster_size": 2}
        ),
        Pattern(
            pattern_type="temporal",
            description="Recurring issues",
            significance=0.7,
            occurrences=3,
            first_seen=base_time - timedelta(hours=1),
            last_seen=base_time,
            related_issues=["Missing prerequisites"],
            metadata={"sequence_length": 2}
        )
    ]

@pytest.fixture
def sample_recovery_actions():
    base_time = datetime.now()
    return [
        {
            "id": "recovery_1",
            "status": "completed",
            "start_time": base_time - timedelta(minutes=30),
            "end_time": base_time - timedelta(minutes=25)
        },
        {
            "id": "recovery_2",
            "status": "failed",
            "start_time": base_time - timedelta(minutes=20),
            "end_time": base_time - timedelta(minutes=18)
        },
        {
            "id": "recovery_3",
            "status": "completed",
            "start_time": base_time - timedelta(minutes=10),
            "end_time": base_time - timedelta(minutes=8)
        }
    ]

def test_empty_metrics(monitoring_service):
    """Test metrics calculation with no data"""
    metrics = monitoring_service.calculate_metrics([], [], [])
    assert len(metrics) == 0

def test_validation_success_rate(
    monitoring_service,
    sample_validation_results
):
    """Test validation success rate calculation"""
    metrics = monitoring_service.calculate_metrics(
        sample_validation_results,
        [],
        []
    )
    
    metric = metrics.get(MetricType.VALIDATION_SUCCESS_RATE)
    assert metric is not None
    assert metric.value == pytest.approx(2/3)  # 2 successful out of 3
    assert metric.metadata["total_validations"] == 3
    assert metric.metadata["successful_validations"] == 2

def test_recovery_success_rate(
    monitoring_service,
    sample_recovery_actions
):
    """Test recovery success rate calculation"""
    metrics = monitoring_service.calculate_metrics(
        [],
        [],
        sample_recovery_actions
    )
    
    metric = metrics.get(MetricType.RECOVERY_SUCCESS_RATE)
    assert metric is not None
    assert metric.value == pytest.approx(2/3)  # 2 completed out of 3
    assert metric.metadata["total_recoveries"] == 3
    assert metric.metadata["successful_recoveries"] == 2

def test_pattern_detection_rate(
    monitoring_service,
    sample_validation_results,
    sample_patterns
):
    """Test pattern detection rate calculation"""
    metrics = monitoring_service.calculate_metrics(
        sample_validation_results,
        sample_patterns,
        []
    )
    
    metric = metrics.get(MetricType.PATTERN_DETECTION_RATE)
    assert metric is not None
    assert metric.value == pytest.approx(2/3)  # 2 patterns for 3 validations
    assert metric.metadata["total_validations"] == 3
    assert metric.metadata["detected_patterns"] == 2

def test_average_confidence_score(
    monitoring_service,
    sample_validation_results
):
    """Test average confidence score calculation"""
    metrics = monitoring_service.calculate_metrics(
        sample_validation_results,
        [],
        []
    )
    
    metric = metrics.get(MetricType.AVERAGE_CONFIDENCE_SCORE)
    assert metric is not None
    assert metric.value == pytest.approx(0.85)  # (0.9 + 0.8 + 0.85) / 3
    assert "score_distribution" in metric.metadata

def test_critical_failure_rate(
    monitoring_service,
    sample_validation_results
):
    """Test critical failure rate calculation"""
    metrics = monitoring_service.calculate_metrics(
        sample_validation_results,
        [],
        []
    )
    
    metric = metrics.get(MetricType.CRITICAL_FAILURE_RATE)
    assert metric is not None
    assert metric.value == pytest.approx(1/3)  # 1 critical failure out of 3
    assert metric.metadata["total_validations"] == 3
    assert metric.metadata["critical_failures"] == 1

def test_recovery_time(
    monitoring_service,
    sample_recovery_actions
):
    """Test average recovery time calculation"""
    metrics = monitoring_service.calculate_metrics(
        [],
        [],
        sample_recovery_actions
    )
    
    metric = metrics.get(MetricType.RECOVERY_TIME)
    assert metric is not None
    # Average of completed recoveries: (5 + 2) / 2 = 3.5 minutes = 210 seconds
    assert metric.value == pytest.approx(210, abs=1)
    assert "time_distribution" in metric.metadata

def test_metric_history(
    monitoring_service,
    sample_validation_results
):
    """Test metric history tracking"""
    # Calculate metrics twice
    monitoring_service.calculate_metrics(sample_validation_results, [], [])
    monitoring_service.calculate_metrics(sample_validation_results, [], [])
    
    history = monitoring_service.get_metric_history(MetricType.VALIDATION_SUCCESS_RATE)
    assert len(history) == 2
    assert all(isinstance(m, PerformanceMetric) for m in history)
    assert history[0].timestamp <= history[1].timestamp

def test_alert_checking(monitoring_service):
    """Test alert threshold checking"""
    metrics = {
        MetricType.VALIDATION_SUCCESS_RATE: PerformanceMetric(
            metric_type=MetricType.VALIDATION_SUCCESS_RATE,
            value=0.7,  # Below threshold of 0.8
            timestamp=datetime.now(),
            window_size=timedelta(hours=24),
            metadata={"total_validations": 10}
        ),
        MetricType.CRITICAL_FAILURE_RATE: PerformanceMetric(
            metric_type=MetricType.CRITICAL_FAILURE_RATE,
            value=0.3,  # Above threshold of 0.2
            timestamp=datetime.now(),
            window_size=timedelta(hours=24),
            metadata={"total_validations": 10}
        )
    }
    
    alerts = monitoring_service.check_alerts(metrics)
    assert len(alerts) == 2
    
    alert_types = {a["metric_type"] for a in alerts}
    assert MetricType.VALIDATION_SUCCESS_RATE in alert_types
    assert MetricType.CRITICAL_FAILURE_RATE in alert_types

def test_time_window_filtering(
    monitoring_service,
    sample_validation_results
):
    """Test metric calculation with time window filtering"""
    # Use a small window that excludes older results
    window_size = timedelta(minutes=15)
    metrics = monitoring_service.calculate_metrics(
        sample_validation_results,
        [],
        [],
        window_size=window_size
    )
    
    metric = metrics.get(MetricType.VALIDATION_SUCCESS_RATE)
    assert metric is not None
    assert metric.value == 1.0  # Only the most recent validation is included
    assert metric.metadata["total_validations"] == 1

def test_score_distribution(
    monitoring_service,
    sample_validation_results
):
    """Test confidence score distribution calculation"""
    metrics = monitoring_service.calculate_metrics(
        sample_validation_results,
        [],
        []
    )
    
    metric = metrics.get(MetricType.AVERAGE_CONFIDENCE_SCORE)
    assert metric is not None
    distribution = metric.metadata["score_distribution"]
    
    assert "0.8" in distribution
    assert "0.9" in distribution
    assert sum(distribution.values()) == 3  # Total number of validations 