# Performance Monitoring System

The Performance Monitoring System is a critical component of the Self-Improving RAG System that tracks, analyzes, and alerts on various performance metrics. It helps maintain system health and identify areas for improvement.

## Overview

The system monitors several key performance indicators:

1. **Validation Success Rate**: Percentage of successful validations
2. **Recovery Success Rate**: Percentage of successful recovery actions
3. **Pattern Detection Rate**: Rate of pattern detection in validation issues
4. **Average Confidence Score**: Mean confidence score across validations
5. **Critical Failure Rate**: Rate of critical validation failures
6. **Recovery Time**: Average time taken for recovery actions

## Components

### Metric Types

The system tracks various metric types:

```python
class MetricType(Enum):
    VALIDATION_SUCCESS_RATE = "validation_success_rate"
    RECOVERY_SUCCESS_RATE = "recovery_success_rate"
    PATTERN_DETECTION_RATE = "pattern_detection_rate"
    AVERAGE_CONFIDENCE_SCORE = "average_confidence_score"
    CRITICAL_FAILURE_RATE = "critical_failure_rate"
    RECOVERY_TIME = "recovery_time"
```

### Performance Metric

Each metric measurement includes:

- `metric_type`: Type of the metric being measured
- `value`: Numerical value of the metric
- `timestamp`: When the measurement was taken
- `window_size`: Time window for the measurement
- `metadata`: Additional metric-specific information

### Performance Monitoring Service

The `PerformanceMonitoringService` provides:

1. **Metric Calculation**:
   - Calculates metrics over specified time windows
   - Handles different types of input data
   - Maintains metric history

2. **Alert Management**:
   - Configurable alert thresholds
   - Automated alert generation
   - Context-aware alerting

3. **Historical Analysis**:
   - Metric history tracking
   - Time-based filtering
   - Trend analysis

## Usage

```python
from src.services.performance_monitoring import PerformanceMonitoringService, MetricType

# Initialize service
monitoring = PerformanceMonitoringService()

# Calculate metrics
metrics = monitoring.calculate_metrics(
    validation_results=validation_results,
    detected_patterns=patterns,
    recovery_actions=recoveries,
    window_size=timedelta(hours=24)
)

# Check for alerts
alerts = monitoring.check_alerts(metrics)

# Get metric history
history = monitoring.get_metric_history(
    metric_type=MetricType.VALIDATION_SUCCESS_RATE,
    start_time=datetime.now() - timedelta(days=7),
    end_time=datetime.now()
)
```

## Configuration

The service includes configurable alert thresholds:

```python
alert_thresholds = {
    MetricType.VALIDATION_SUCCESS_RATE: 0.8,   # 80% success rate
    MetricType.RECOVERY_SUCCESS_RATE: 0.7,     # 70% success rate
    MetricType.PATTERN_DETECTION_RATE: 0.6,    # 60% detection rate
    MetricType.AVERAGE_CONFIDENCE_SCORE: 0.75, # 0.75 confidence
    MetricType.CRITICAL_FAILURE_RATE: 0.2,     # 20% critical rate
    MetricType.RECOVERY_TIME: 300              # 5 minutes
}
```

## Metric Details

### 1. Validation Success Rate
- Tracks the ratio of successful validations
- Helps identify systemic validation issues
- Includes metadata about total validations

### 2. Recovery Success Rate
- Monitors effectiveness of recovery actions
- Tracks completion status of recoveries
- Includes metadata about recovery attempts

### 3. Pattern Detection Rate
- Measures effectiveness of pattern recognition
- Relates patterns to validation volume
- Includes metadata about pattern types

### 4. Average Confidence Score
- Tracks overall validation confidence
- Includes score distribution analysis
- Helps identify validation quality trends

### 5. Critical Failure Rate
- Monitors rate of severe validation issues
- Helps identify systemic problems
- Includes failure categorization

### 6. Recovery Time
- Tracks efficiency of recovery actions
- Includes time distribution analysis
- Helps optimize recovery strategies

## Alert System

The alert system provides:

1. **Threshold-Based Alerts**:
   - Configurable thresholds per metric
   - Direction-aware comparisons
   - Contextual alert metadata

2. **Alert Types**:
   - Performance degradation alerts
   - Critical failure alerts
   - Recovery efficiency alerts

3. **Alert Context**:
   - Current metric value
   - Threshold information
   - Relevant metadata
   - Timestamp information

## Integration

The Performance Monitoring System integrates with:

1. **Validation System**: 
   - Receives validation results
   - Tracks validation performance
   - Monitors validation quality

2. **Pattern Recognition**:
   - Monitors pattern detection
   - Tracks pattern significance
   - Analyzes pattern trends

3. **Recovery Management**:
   - Tracks recovery performance
   - Monitors recovery times
   - Analyzes recovery strategies

## Future Improvements

1. **Advanced Analytics**:
   - Machine learning-based anomaly detection
   - Predictive performance modeling
   - Automated threshold adjustment

2. **Visualization**:
   - Real-time metric dashboards
   - Trend visualization
   - Alert visualization

3. **Enhanced Alerting**:
   - Multi-level alert thresholds
   - Alert correlation
   - Automated response suggestions 