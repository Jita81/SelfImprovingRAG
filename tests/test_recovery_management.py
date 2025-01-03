import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.services.recovery_management import (
    RecoveryManagementService,
    RecoveryStrategy,
    RecoveryAction
)
from src.services.pattern_recognition import PatternRecognitionService, Pattern
from src.models.validation_result import ValidationResult

class MockPatternRecognitionService:
    def __init__(self, patterns: List[Pattern] = None):
        self.patterns = patterns or []
        
    def analyze_validation_history(
        self,
        validation_results: List[ValidationResult],
        min_significance: float = 0.3
    ) -> List[Pattern]:
        return [p for p in self.patterns if p.significance >= min_significance]

@pytest.fixture
def sample_validation_result():
    return ValidationResult(
        is_valid=False,
        issues=["Technical level mismatch", "Missing prerequisites"],
        confidence_score=0.7,
        timestamp=datetime.now()
    )

@pytest.fixture
def sample_validation_history():
    base_time = datetime.now()
    return [
        ValidationResult(
            is_valid=False,
            issues=["Technical level mismatch"],
            confidence_score=0.6,
            timestamp=base_time - timedelta(hours=2)
        ),
        ValidationResult(
            is_valid=False,
            issues=["Missing prerequisites"],
            confidence_score=0.5,
            timestamp=base_time - timedelta(hours=1)
        )
    ]

@pytest.fixture
def sample_patterns():
    base_time = datetime.now()
    return [
        Pattern(
            pattern_type="semantic",
            description="Similar technical level issues",
            significance=0.8,
            occurrences=3,
            first_seen=base_time - timedelta(hours=2),
            last_seen=base_time,
            related_issues=["Technical level mismatch", "Technical level too high"],
            metadata={"cluster_size": 2, "average_similarity": 0.9}
        ),
        Pattern(
            pattern_type="temporal",
            description="Recurring prerequisite issues",
            significance=0.75,
            occurrences=2,
            first_seen=base_time - timedelta(hours=1),
            last_seen=base_time,
            related_issues=["Missing prerequisites", "Undefined prerequisites"],
            metadata={"sequence_length": 2, "temporal_density": 0.8}
        )
    ]

@pytest.fixture
def recovery_service(sample_patterns):
    pattern_service = MockPatternRecognitionService(sample_patterns)
    return RecoveryManagementService(pattern_service)

def test_analyze_valid_result(recovery_service):
    """Test analyzing a valid validation result"""
    result = ValidationResult(
        is_valid=True,
        issues=[],
        confidence_score=1.0,
        timestamp=datetime.now()
    )
    
    action = recovery_service.analyze_failure(result, [])
    assert action is None

def test_analyze_critical_failure(recovery_service, sample_validation_result):
    """Test analyzing a critical validation failure"""
    # Make it critical by setting high confidence score
    critical_result = ValidationResult(
        is_valid=False,
        issues=sample_validation_result.issues,
        confidence_score=0.9,  # Above critical threshold
        timestamp=datetime.now()
    )
    
    action = recovery_service.analyze_failure(critical_result, [])
    
    assert action is not None
    assert action.strategy == RecoveryStrategy.ROLLBACK
    assert action.priority == 1
    assert action.estimated_impact == 1.0
    assert "knowledge_map" in action.required_resources
    assert "validation_history" in action.required_resources

def test_analyze_pattern_based_failure(
    recovery_service,
    sample_validation_result,
    sample_validation_history
):
    """Test analyzing a failure with matching patterns"""
    action = recovery_service.analyze_failure(
        sample_validation_result,
        sample_validation_history
    )
    
    assert action is not None
    assert action.strategy in [
        RecoveryStrategy.REVALIDATION,
        RecoveryStrategy.INCREMENTAL_FIX
    ]
    assert action.priority in [2, 3]
    assert action.estimated_impact > 0
    assert len(action.required_resources) > 0

def test_analyze_isolated_failure(recovery_service):
    """Test analyzing an isolated failure without patterns"""
    # Create service with no patterns
    service = RecoveryManagementService(MockPatternRecognitionService([]))
    
    result = ValidationResult(
        is_valid=False,
        issues=["Unique issue"],
        confidence_score=0.4,
        timestamp=datetime.now()
    )
    
    action = service.analyze_failure(result, [])
    
    assert action is not None
    assert action.strategy == RecoveryStrategy.INCREMENTAL_FIX
    assert action.priority == 4
    assert action.estimated_impact == result.confidence_score
    assert "knowledge_map" in action.required_resources

def test_execute_recovery_success(recovery_service, sample_validation_result):
    """Test successful recovery execution"""
    action = recovery_service.analyze_failure(sample_validation_result, [])
    context = {"knowledge_map": {}, "validation_system": {}}
    
    success = recovery_service.execute_recovery(action, context)
    assert success
    
    # Check recovery history
    assert len(recovery_service.recovery_history) == 1
    record = recovery_service.recovery_history[0]
    assert record["status"] == "completed"
    assert "start_time" in record
    assert "end_time" in record

def test_execute_recovery_failure(recovery_service, sample_validation_result):
    """Test failed recovery execution"""
    action = recovery_service.analyze_failure(sample_validation_result, [])
    # Missing required context
    context = {}
    
    success = recovery_service.execute_recovery(action, context)
    assert not success
    
    # Check recovery history
    assert len(recovery_service.recovery_history) == 1
    record = recovery_service.recovery_history[0]
    assert record["status"] in ["failed", "error"]
    assert "start_time" in record
    assert "end_time" in record

def test_concurrent_recovery_limit(recovery_service, sample_validation_result):
    """Test concurrent recovery limit"""
    action = recovery_service.analyze_failure(sample_validation_result, [])
    context = {"knowledge_map": {}, "validation_system": {}}
    
    # Fill up active recoveries
    for _ in range(recovery_service.max_concurrent_recoveries):
        recovery_service.execute_recovery(action, context)
    
    # Try one more
    success = recovery_service.execute_recovery(action, context)
    assert not success

def test_recovery_strategy_selection(
    recovery_service,
    sample_validation_result,
    sample_validation_history,
    sample_patterns
):
    """Test recovery strategy selection based on patterns"""
    # Test with temporal pattern
    temporal_result = ValidationResult(
        is_valid=False,
        issues=["Missing prerequisites"],
        confidence_score=0.6,
        timestamp=datetime.now()
    )
    
    action = recovery_service.analyze_failure(temporal_result, sample_validation_history)
    assert action.strategy == RecoveryStrategy.REVALIDATION
    
    # Test with semantic pattern
    semantic_result = ValidationResult(
        is_valid=False,
        issues=["Technical level mismatch"],
        confidence_score=0.6,
        timestamp=datetime.now()
    )
    
    action = recovery_service.analyze_failure(semantic_result, sample_validation_history)
    assert action.strategy == RecoveryStrategy.INCREMENTAL_FIX 