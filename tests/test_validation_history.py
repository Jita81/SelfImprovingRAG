import pytest
from datetime import datetime, timedelta
from src.models.validation_result import ValidationResult
from src.models.validation_history import ValidationHistory
import os
import tempfile
import json
from pathlib import Path

@pytest.fixture
def history():
    return ValidationHistory()

@pytest.fixture
def sample_results():
    return [
        ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now() - timedelta(days=2)
        ),
        ValidationResult(
            is_valid=False,
            issues=["Content too basic", "Missing examples"],
            confidence_score=0.4,
            timestamp=datetime.now() - timedelta(days=1)
        ),
        ValidationResult(
            is_valid=False,
            issues=["Content too basic", "Technical level mismatch"],
            confidence_score=0.5,
            timestamp=datetime.now()
        )
    ]

@pytest.fixture
def temp_storage():
    """Create a temporary file for history storage"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.remove(temp_path)

def test_add_result(history, sample_results):
    """Test adding validation results to history"""
    for result in sample_results:
        history.add_result(result)
    assert len(history.history) == 3

def test_average_confidence_all_time(history, sample_results):
    """Test calculating average confidence score across all time"""
    for result in sample_results:
        history.add_result(result)
    avg = history.get_average_confidence()
    assert avg == pytest.approx(0.6, rel=1e-6)

def test_average_confidence_time_window(history, sample_results):
    """Test calculating average confidence score within time window"""
    for result in sample_results:
        history.add_result(result)
    # Only include last 36 hours (should exclude first result)
    avg = history.get_average_confidence(timedelta(hours=36))
    assert avg == pytest.approx(0.45, rel=1e-6)

def test_common_issues(history, sample_results):
    """Test identifying common validation issues"""
    for result in sample_results:
        history.add_result(result)
    common = history.get_common_issues()
    assert len(common) == 3
    assert common[0] == ("Content too basic", 2)  # Most common issue
    assert ("Missing examples", 1) in common
    assert ("Technical level mismatch", 1) in common

def test_empty_history(history):
    """Test behavior with empty history"""
    assert history.get_average_confidence() == 0.0
    assert history.get_common_issues() == [] 

def test_issue_categories(history, sample_results):
    """Test issue categorization"""
    for result in sample_results:
        history.add_result(result)
        
    categories = history.get_issue_categories()
    assert "categories" in categories
    assert "total_validations" in categories
    assert "failed_validations" in categories
    
    # Check category counts
    cat = categories["categories"]
    assert cat["technical_level"] == 1  # "Technical level mismatch"
    assert cat["content_coverage"] == 1  # "Missing examples"
    assert cat["system_errors"] == 0  # No system errors
    assert cat["improvement_suggestions"] == 2  # Two "Content too basic" issues
    
    # Check validation counts
    assert categories["total_validations"] == 3
    assert categories["failed_validations"] == 2  # Two invalid results

def test_trend_summary(history, sample_results):
    """Test comprehensive trend summary"""
    for result in sample_results:
        history.add_result(result)
        
    summary = history.get_trend_summary()
    assert "average_confidence" in summary
    assert "failure_rate" in summary
    assert "categories" in summary
    assert "common_issues" in summary
    
    assert 0 <= summary["average_confidence"] <= 1.0
    assert summary["failure_rate"] == 2/3  # Two out of three validations failed
    assert len(summary["common_issues"]) > 0

def test_empty_trend_summary(history):
    """Test trend summary with empty history"""
    summary = history.get_trend_summary()
    assert summary["average_confidence"] == 0.0
    assert summary["failure_rate"] == 0.0
    assert all(count == 0 for count in summary["categories"].values())
    assert len(summary["common_issues"]) == 0

def test_system_error_categorization(history):
    """Test categorization of system errors"""
    error_result = ValidationResult(
        is_valid=False,
        issues=["Validation error: API timeout", "System error occurred"],
        confidence_score=0.0
    )
    history.add_result(error_result)
    
    categories = history.get_issue_categories()
    assert categories["categories"]["system_errors"] == 2  # Both issues are system errors 

def test_time_series_analysis(history, sample_results):
    """Test time-based trend analysis"""
    for result in sample_results:
        history.add_result(result)
        
    # Analyze with 1-day periods
    time_series = history.get_time_series_analysis(timedelta(days=1))
    assert len(time_series) == 3  # Should have 3 days of data
    
    # Check structure of each data point
    for point in time_series:
        assert "timestamp" in point
        assert "validation_count" in point
        assert "failure_rate" in point
        assert "confidence_avg" in point
        assert "categories" in point
        assert isinstance(point["categories"], dict)
        
    # Check specific data points
    latest = time_series[-1]  # Most recent day
    assert latest["validation_count"] == 1
    assert latest["failure_rate"] == 1.0  # One failed validation
    assert latest["confidence_avg"] == 0.5
    assert latest["categories"]["technical_level"] == 1
    assert latest["categories"]["improvement_suggestions"] == 1

def test_time_series_empty_periods(history, sample_results):
    """Test time series analysis with empty periods"""
    # Add results with gaps between them
    history.add_result(sample_results[0])  # Day 1
    history.add_result(sample_results[2])  # Day 3
    
    time_series = history.get_time_series_analysis(timedelta(days=1))
    assert len(time_series) == 2  # Should only include days with data
    
    # Verify first and last points
    first = time_series[0]
    assert first["validation_count"] == 1
    assert first["failure_rate"] == 0.0  # Valid result
    
    last = time_series[-1]
    assert last["validation_count"] == 1
    assert last["failure_rate"] == 1.0  # Invalid result

def test_time_series_custom_period(history, sample_results):
    """Test time series analysis with custom period length"""
    for result in sample_results:
        history.add_result(result)
        
    # Analyze with 2-day periods
    time_series = history.get_time_series_analysis(timedelta(days=2))
    assert len(time_series) == 2  # Should combine into 2 periods
    
    # First period should contain the first two results
    first_period = time_series[0]
    assert first_period["validation_count"] == 2
    assert first_period["failure_rate"] == 0.5  # One valid, one invalid
    
    # Second period should contain the last result
    second_period = time_series[1]
    assert second_period["validation_count"] == 1
    assert second_period["failure_rate"] == 1.0  # One invalid result 

def test_trend_detection_insufficient_data(history):
    """Test trend detection with insufficient data"""
    # Add just a few results
    for i in range(3):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    trends = history.detect_trends(window_size=5)
    assert trends["confidence_trend"] == "insufficient_data"
    assert trends["failure_trend"] == "insufficient_data"
    assert trends["issue_trends"] == {}
    assert trends["alerts"] == []

def test_trend_detection_stable(history):
    """Test trend detection with stable metrics"""
    # Add 10 similar results
    for i in range(10):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    trends = history.detect_trends(window_size=5)
    assert trends["confidence_trend"] == "no_change"
    assert trends["failure_trend"] == "no_change"
    assert all(trend == "no_change" for trend in trends["issue_trends"].values())
    assert trends["alerts"] == []

def test_trend_detection_significant_change(history):
    """Test trend detection with significant changes"""
    # First 10 results with high confidence
    for i in range(10):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Last 5 results with low confidence and failures
    for i in range(5):
        result = ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch", "Content too basic"],
            confidence_score=0.3,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    trends = history.detect_trends(window_size=5)
    assert trends["confidence_trend"] == "decreasing"
    assert trends["failure_trend"] == "increasing"
    assert trends["issue_trends"]["technical_level"] == "increasing"
    assert len(trends["alerts"]) > 0  # Should have alerts about the changes

def test_trend_detection_custom_threshold(history):
    """Test trend detection with custom sensitivity threshold"""
    # First 10 results with high confidence
    for i in range(10):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.90,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Last 5 results with slightly lower confidence
    for i in range(5):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.87,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # With high threshold, should not detect change
    trends_high = history.detect_trends(window_size=5, threshold=2.0)
    assert trends_high["confidence_trend"] == "no_change"
    assert len(trends_high["alerts"]) == 0
    
    # With low threshold, should detect change
    trends_low = history.detect_trends(window_size=5, threshold=0.5)
    assert trends_low["confidence_trend"] == "decreasing"
    assert len(trends_low["alerts"]) > 0 

def test_recommendations_insufficient_data(history):
    """Test recommendations with insufficient data"""
    # Add just a few results
    for i in range(3):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
        
    recommendations = history.get_recommendations()
    assert recommendations == []  # Should have no recommendations with insufficient data

def test_recommendations_stable_system(history):
    """Test recommendations with stable system"""
    # Add 10 good results
    for i in range(10):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
        
    recommendations = history.get_recommendations()
    assert recommendations == []  # Should have no recommendations for stable system

def test_recommendations_quality_issues(history):
    """Test recommendations with quality issues"""
    # First 10 results with high confidence
    for i in range(10):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Last 5 results with declining quality
    for i in range(5):
        result = ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch", "Missing examples"],
            confidence_score=0.3,
            timestamp=datetime.now()
        )
        history.add_result(result)
        
    recommendations = history.get_recommendations()
    assert len(recommendations) > 0
    
    # Check recommendation structure
    for rec in recommendations:
        assert "category" in rec
        assert "priority" in rec
        assert "issue" in rec
        assert "recommendation" in rec
        assert "evidence" in rec
        assert rec["priority"] in ["high", "medium", "low"]
        
    # Should have quality recommendations
    quality_recs = [r for r in recommendations if r["category"] == "quality"]
    assert len(quality_recs) > 0
    assert any(r["issue"] == "Declining validation confidence" for r in quality_recs)
    
    # Should have technical recommendations
    tech_recs = [r for r in recommendations if r["category"] == "technical"]
    assert len(tech_recs) > 0
    
    # Verify priority ordering
    priorities = [r["priority"] for r in recommendations]
    assert priorities == sorted(priorities, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x])

def test_recommendations_system_errors(history):
    """Test recommendations with system errors"""
    # Add some normal results
    for i in range(10):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Add system errors
    for i in range(3):
        result = ValidationResult(
            is_valid=False,
            issues=["Validation error: API timeout", "System error occurred"],
            confidence_score=0.0,
            timestamp=datetime.now()
        )
        history.add_result(result)
        
    recommendations = history.get_recommendations()
    
    # Should have system recommendations
    system_recs = [r for r in recommendations if r["category"] == "system"]
    assert len(system_recs) > 0
    assert system_recs[0]["priority"] == "high"  # System errors should be high priority 

def test_history_persistence(temp_storage, sample_results):
    """Test saving and loading validation history"""
    # Create history with storage
    history = ValidationHistory(storage_path=temp_storage)
    
    # Add results and verify they're saved
    for result in sample_results:
        history.add_result(result)
        
    assert os.path.exists(temp_storage)
    
    # Load file and verify contents
    with open(temp_storage, 'r') as f:
        saved_data = json.load(f)
    assert len(saved_data) == len(sample_results)
    
    # Create new history instance and verify it loads the data
    new_history = ValidationHistory(storage_path=temp_storage)
    assert len(new_history.history) == len(sample_results)
    
    # Verify loaded data matches original
    for orig, loaded in zip(sample_results, new_history.history):
        assert orig.is_valid == loaded.is_valid
        assert orig.issues == loaded.issues
        assert orig.confidence_score == loaded.confidence_score
        assert orig.timestamp.isoformat() == loaded.timestamp.isoformat()

def test_history_clear(temp_storage, sample_results):
    """Test clearing persistent history"""
    history = ValidationHistory(storage_path=temp_storage)
    
    # Add results
    for result in sample_results:
        history.add_result(result)
    
    assert os.path.exists(temp_storage)
    
    # Clear history
    history.clear_history()
    assert len(history.history) == 0
    assert not os.path.exists(temp_storage)
    
    # Verify new instance starts fresh
    new_history = ValidationHistory(storage_path=temp_storage)
    assert len(new_history.history) == 0

def test_corrupted_storage(temp_storage):
    """Test handling of corrupted storage file"""
    # Create corrupted JSON file
    with open(temp_storage, 'w') as f:
        f.write("{ invalid json")
    
    # Should handle corrupted file gracefully
    history = ValidationHistory(storage_path=temp_storage)
    assert len(history.history) == 0
    
    # Should still be able to add new results
    result = ValidationResult(
        is_valid=True,
        issues=[],
        confidence_score=0.9,
        timestamp=datetime.now()
    )
    history.add_result(result)
    assert len(history.history) == 1

def test_no_persistence():
    """Test history without persistence"""
    history = ValidationHistory()  # No storage path
    
    result = ValidationResult(
        is_valid=True,
        issues=[],
        confidence_score=0.9,
        timestamp=datetime.now()
    )
    history.add_result(result)
    
    # Should work normally without persistence
    assert len(history.history) == 1 

def test_history_rotation_age(temp_storage):
    """Test rotating history entries based on age"""
    history = ValidationHistory(storage_path=temp_storage, max_age_days=1, max_entries=100)
    
    # Add old entries
    old_time = datetime.now() - timedelta(days=2)
    for i in range(3):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=old_time
        )
        history.add_result(result)
    
    # Add recent entries
    for i in range(2):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Verify active history only contains recent entries
    assert len(history.history) == 2
    
    # Verify archive exists and contains old entries
    archive_path = history._get_archive_path()
    assert os.path.exists(archive_path)
    
    with open(archive_path, 'r') as f:
        archived_data = json.load(f)
    assert len(archived_data) == 3

def test_history_rotation_size(temp_storage):
    """Test rotating history entries based on size limit"""
    history = ValidationHistory(storage_path=temp_storage, max_age_days=30, max_entries=3)
    
    # Add more entries than the limit
    for i in range(5):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Verify active history respects size limit
    assert len(history.history) == 3
    
    # Verify archive contains overflow entries
    archive_path = history._get_archive_path()
    assert os.path.exists(archive_path)
    
    with open(archive_path, 'r') as f:
        archived_data = json.load(f)
    assert len(archived_data) == 2

def test_clear_history_with_archive(temp_storage, sample_results):
    """Test clearing history with archive option"""
    history = ValidationHistory(storage_path=temp_storage, max_age_days=1)
    
    # Add some old and new results
    old_time = datetime.now() - timedelta(days=2)
    for result in sample_results:
        result.timestamp = old_time
        history.add_result(result)
    
    # Verify archive was created
    archive_path = history._get_archive_path()
    assert os.path.exists(archive_path)
    
    # Clear history including archive
    history.clear_history(include_archive=True)
    assert len(history.history) == 0
    assert not os.path.exists(temp_storage)
    assert not os.path.exists(archive_path)

def test_history_rotation_preserves_order(temp_storage):
    """Test that history rotation preserves chronological order"""
    history = ValidationHistory(storage_path=temp_storage, max_age_days=1, max_entries=3)
    
    # Add mixed old and new entries
    timestamps = [
        datetime.now() - timedelta(days=2),
        datetime.now() - timedelta(hours=12),
        datetime.now()
    ]
    
    for ts in timestamps:
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=ts
        )
        history.add_result(result)
    
    # Verify active history maintains chronological order
    assert len(history.history) == 2  # Only recent entries
    assert history.history[0].timestamp == timestamps[1]
    assert history.history[1].timestamp == timestamps[2] 

def test_archive_analysis_empty(history):
    """Test archive analysis with empty history"""
    analysis = history.analyze_archive()
    assert analysis["total_validations"] == 0
    assert analysis["historical_confidence"] == []
    assert analysis["recurring_issues"] == []
    assert analysis["stability_metrics"]["error_rate"] == 0.0
    assert analysis["improvement_indicators"]["trend"] == "insufficient_data"

def test_archive_analysis_active_only(history, sample_results):
    """Test archive analysis with only active history"""
    for result in sample_results:
        history.add_result(result)
        
    analysis = history.analyze_archive()
    assert analysis["total_validations"] == 3
    assert len(analysis["historical_confidence"]) > 0
    assert len(analysis["recurring_issues"]) > 0
    assert 0 <= analysis["stability_metrics"]["error_rate"] <= 1.0
    assert 0 <= analysis["stability_metrics"]["consistency_score"] <= 1.0

def test_archive_analysis_with_archive(temp_storage):
    """Test archive analysis with both active and archived data"""
    history = ValidationHistory(storage_path=temp_storage, max_age_days=1)
    
    # Add old entries (will be archived)
    old_time = datetime.now() - timedelta(days=2)
    for i in range(3):
        result = ValidationResult(
            is_valid=True,
            issues=["Old issue"],
            confidence_score=0.7,
            timestamp=old_time
        )
        history.add_result(result)
    
    # Add recent entries
    for i in range(2):
        result = ValidationResult(
            is_valid=False,
            issues=["Recent issue"],
            confidence_score=0.4,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    analysis = history.analyze_archive()
    assert analysis["total_validations"] == 5  # All entries included
    
    # Check recurring issues
    recurring = [issue for issue in analysis["recurring_issues"] if issue["count"] > 1]
    assert len(recurring) > 0
    
    # Verify historical confidence periods
    assert len(analysis["historical_confidence"]) > 0
    for period in analysis["historical_confidence"]:
        assert "period_start" in period
        assert "average_confidence" in period
        assert "validation_count" in period

def test_archive_analysis_time_window(temp_storage):
    """Test archive analysis with time window filtering"""
    history = ValidationHistory(storage_path=temp_storage, max_age_days=30)
    
    # Add entries across different time periods
    timestamps = [
        datetime.now() - timedelta(days=10),
        datetime.now() - timedelta(days=5),
        datetime.now() - timedelta(days=1)
    ]
    
    for ts in timestamps:
        result = ValidationResult(
            is_valid=True,
            issues=[f"Issue at {ts.isoformat()}"],
            confidence_score=0.8,
            timestamp=ts
        )
        history.add_result(result)
    
    # Analyze with 3-day window
    recent_analysis = history.analyze_archive(timedelta(days=3))
    assert recent_analysis["total_validations"] == 1  # Only most recent entry
    
    # Analyze with 7-day window
    week_analysis = history.analyze_archive(timedelta(days=7))
    assert week_analysis["total_validations"] == 2  # Two most recent entries
    
    # Analyze all time
    full_analysis = history.analyze_archive()
    assert full_analysis["total_validations"] == 3  # All entries 

def test_pattern_recognition_empty(history):
    """Test pattern recognition with empty history"""
    patterns = history.get_validation_patterns()
    assert patterns == []

def test_pattern_recognition_insufficient_data(history):
    """Test pattern recognition with insufficient data"""
    result = ValidationResult(
        is_valid=True,
        issues=[],
        confidence_score=0.9,
        timestamp=datetime.now()
    )
    history.add_result(result)
    
    patterns = history.get_validation_patterns(min_occurrences=2)
    assert patterns == []

def test_issue_sequence_pattern(history):
    """Test recognition of recurring issue sequences"""
    # Add a repeating pattern of validation results
    sequence = [
        ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch"],
            confidence_score=0.4,
            timestamp=datetime.now()
        ),
        ValidationResult(
            is_valid=False,
            issues=["Missing examples"],
            confidence_score=0.5,
            timestamp=datetime.now()
        )
    ]
    
    # Add sequence twice
    for _ in range(2):
        for result in sequence:
            history.add_result(result)
    
    patterns = history.get_validation_patterns()
    
    # Should find the repeating sequence
    sequence_patterns = [p for p in patterns if p["pattern_type"] == "issue_sequence"]
    assert len(sequence_patterns) > 0
    
    pattern = sequence_patterns[0]
    assert pattern["occurrences"] >= 2
    assert "Technical level mismatch" in pattern["description"]
    assert "Missing examples" in pattern["description"]
    assert 0 <= pattern["significance"] <= 1.0

def test_confidence_pattern(history):
    """Test recognition of confidence score patterns"""
    # Add consistently declining confidence scores
    scores = [0.9, 0.7, 0.5, 0.3]
    for score in scores:
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=score,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    patterns = history.get_validation_patterns()
    
    # Should find the confidence decline pattern
    confidence_patterns = [p for p in patterns if p["pattern_type"] == "confidence_pattern"]
    assert len(confidence_patterns) > 0
    
    pattern = confidence_patterns[0]
    assert "declining" in pattern["description"].lower()
    assert pattern["occurrences"] == len(scores) - 1
    assert 0 <= pattern["significance"] <= 1.0

def test_timing_pattern(history):
    """Test recognition of timing patterns"""
    # Add results at regular intervals
    interval = timedelta(hours=1)
    base_time = datetime.now()
    
    for i in range(5):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=base_time + i * interval
        )
        history.add_result(result)
    
    patterns = history.get_validation_patterns()
    
    # Should find the regular timing pattern
    timing_patterns = [p for p in patterns if p["pattern_type"] == "timing_pattern"]
    assert len(timing_patterns) > 0
    
    pattern = timing_patterns[0]
    assert "1.0 hours" in pattern["description"]
    assert pattern["occurrences"] == 4  # Number of intervals
    assert 0 <= pattern["significance"] <= 1.0

def test_multiple_patterns(history):
    """Test recognition of multiple pattern types"""
    # Add results that exhibit multiple patterns
    base_time = datetime.now()
    interval = timedelta(hours=1)
    
    sequence = [
        ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch"],
            confidence_score=0.8,
            timestamp=base_time
        ),
        ValidationResult(
            is_valid=False,
            issues=["Missing examples"],
            confidence_score=0.6,
            timestamp=base_time + interval
        )
    ]
    
    # Repeat sequence with declining confidence
    for i in range(2):
        for j, result in enumerate(sequence):
            adjusted_result = ValidationResult(
                is_valid=result.is_valid,
                issues=result.issues,
                confidence_score=result.confidence_score - (i * 0.2),
                timestamp=base_time + (i * 2 + j) * interval
            )
            history.add_result(adjusted_result)
    
    patterns = history.get_validation_patterns()
    
    # Should find multiple pattern types
    pattern_types = {p["pattern_type"] for p in patterns}
    assert len(pattern_types) >= 2  # Should find at least 2 types of patterns
    
    # Patterns should be sorted by significance
    significances = [p["significance"] for p in patterns]
    assert significances == sorted(significances, reverse=True)

def test_pattern_significance(history):
    """Test pattern significance calculation"""
    # Add a very clear pattern
    sequence = [
        ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch"],
            confidence_score=0.4,
            timestamp=datetime.now()
        ),
        ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
    ]
    
    # Repeat sequence multiple times
    for _ in range(4):  # High number of repetitions
        for result in sequence:
            history.add_result(result)
    
    patterns = history.get_validation_patterns()
    
    # The pattern should have high significance
    assert any(p["significance"] > 0.7 for p in patterns)
    
    # Add some random results to dilute the pattern
    for _ in range(10):
        result = ValidationResult(
            is_valid=True,
            issues=[],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Get patterns again
    diluted_patterns = history.get_validation_patterns()
    
    # The pattern significance should be lower now
    matching_pattern = next(
        p for p in diluted_patterns 
        if p["pattern_type"] == "issue_sequence" and "Technical level mismatch" in p["description"]
    )
    assert matching_pattern["significance"] < 0.7 

def test_find_related_issues_empty(history):
    """Test finding related issues with empty history"""
    related = history.find_related_issues("Technical level mismatch")
    assert related == []

def test_find_related_issues_no_matches(history):
    """Test finding related issues with no matches"""
    result = ValidationResult(
        is_valid=False,
        issues=["System error: timeout"],
        confidence_score=0.4,
        timestamp=datetime.now()
    )
    history.add_result(result)
    
    related = history.find_related_issues("Technical level mismatch", min_similarity=0.7)
    assert related == []

def test_find_related_issues_exact_match(history):
    """Test finding related issues with exact matches"""
    base_time = datetime.now()
    issues = [
        "Technical level too advanced",
        "Technical level mismatch",
        "Technical level too basic"
    ]
    
    for i, issue in enumerate(issues):
        result = ValidationResult(
            is_valid=False,
            issues=[issue],
            confidence_score=0.4,
            timestamp=base_time + timedelta(hours=i)
        )
        history.add_result(result)
    
    related = history.find_related_issues("Technical level mismatch", min_similarity=0.7)
    assert len(related) == 2  # Should find both other technical level issues
    
    # Check structure and sorting
    for item in related:
        assert "issue" in item
        assert "similarity" in item
        assert "occurrences" in item
        assert "first_seen" in item
        assert "last_seen" in item
        assert item["similarity"] >= 0.7
        assert item["occurrences"] == 1
    
    # Should be sorted by similarity
    similarities = [item["similarity"] for item in related]
    assert similarities == sorted(similarities, reverse=True)

def test_find_related_issues_partial_match(history):
    """Test finding related issues with partial matches"""
    issues = [
        "Content missing examples",
        "Missing code examples",
        "Examples needed",
        "System error occurred"  # Unrelated issue
    ]
    
    for issue in issues:
        result = ValidationResult(
            is_valid=False,
            issues=[issue],
            confidence_score=0.4,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    related = history.find_related_issues("Missing examples", min_similarity=0.5)
    assert len(related) == 3  # Should find all example-related issues
    
    # Unrelated issue should have lower similarity
    similarities = [item["similarity"] for item in related]
    assert min(similarities) >= 0.5

def test_get_issue_clusters_empty(history):
    """Test getting issue clusters with empty history"""
    clusters = history.get_issue_clusters()
    assert clusters == []

def test_get_issue_clusters_single_cluster(history):
    """Test getting issue clusters with a single cluster"""
    issues = [
        "Technical level too advanced",
        "Technical level mismatch",
        "Technical level too basic",
        "System error occurred"  # Should be in different cluster
    ]
    
    for issue in issues:
        result = ValidationResult(
            is_valid=False,
            issues=[issue],
            confidence_score=0.4,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    clusters = history.get_issue_clusters(min_similarity=0.7)
    assert len(clusters) > 0
    
    # Find technical level cluster
    tech_cluster = next(
        c for c in clusters 
        if any("technical level" in issue.lower() for issue in c["issues"])
    )
    
    assert len(tech_cluster["issues"]) == 3  # All technical level issues
    assert tech_cluster["total_occurrences"] == 3
    assert "technical" in tech_cluster["common_terms"]
    assert "level" in tech_cluster["common_terms"]

def test_get_issue_clusters_multiple_clusters(history):
    """Test getting issue clusters with multiple distinct clusters"""
    issue_groups = [
        # Technical level cluster
        ["Technical level too advanced", "Technical level too basic"],
        # Examples cluster
        ["Missing examples", "Code examples needed", "Examples incomplete"],
        # Error cluster
        ["System error", "Runtime error", "Error in processing"]
    ]
    
    for group in issue_groups:
        for issue in group:
            result = ValidationResult(
                is_valid=False,
                issues=[issue],
                confidence_score=0.4,
                timestamp=datetime.now()
            )
            history.add_result(result)
    
    clusters = history.get_issue_clusters(min_similarity=0.6)
    
    # Should find all three clusters
    assert len(clusters) == 3
    
    # Verify cluster properties
    for cluster in clusters:
        assert len(cluster["issues"]) > 0
        assert cluster["total_occurrences"] > 0
        assert cluster["time_span"] >= 0
        assert len(cluster["common_terms"]) > 0
    
    # Clusters should be sorted by total occurrences
    occurrences = [c["total_occurrences"] for c in clusters]
    assert occurrences == sorted(occurrences, reverse=True)

def test_get_issue_clusters_overlapping(history):
    """Test getting issue clusters with potential overlap"""
    issues = [
        "Technical content too advanced",
        "Technical level mismatch",
        "Content missing examples",
        "Technical examples needed"
    ]
    
    for issue in issues:
        result = ValidationResult(
            is_valid=False,
            issues=[issue],
            confidence_score=0.4,
            timestamp=datetime.now()
        )
        history.add_result(result)
    
    # Test with different similarity thresholds
    high_threshold_clusters = history.get_issue_clusters(min_similarity=0.8)
    low_threshold_clusters = history.get_issue_clusters(min_similarity=0.5)
    
    # Higher threshold should produce more distinct clusters
    assert len(high_threshold_clusters) >= len(low_threshold_clusters)
    
    # Each issue should appear in at least one cluster
    all_issues = set()
    for cluster in high_threshold_clusters:
        all_issues.update(cluster["issues"])
    assert len(all_issues) == len(issues) 