# leaderboard_social Testing Documentation

## Overview
This document outlines the testing strategy, test scenarios, and testing procedures for the leaderboard_social module.

## Testing Strategy

### Testing Pyramid
```
    End-to-End Tests (5%)
      Integration Tests (15%)
        Unit Tests (80%)
```

### Testing Principles
- **TDD Approach**: Write tests before implementation (Red-Green-Refactor)
- **Comprehensive Coverage**: Aim for >90% code coverage
- **Test Isolation**: Each test should be independent
- **Fast Feedback**: Unit tests should run quickly
- **Readable Tests**: Tests should be self-documenting

## Test Categories

### Unit Tests (80% of tests)
Test individual components in isolation:
- Domain entities and value objects
- Application services
- Individual repository methods
- Utility functions

### Integration Tests (15% of tests)
Test component interactions:
- Service + Repository integration
- Event publishing/subscription
- External API integration
- Data flow between layers

### End-to-End Tests (5% of tests)
Test complete workflows:
- Full business scenarios
- API endpoint functionality
- Error handling flows
- Performance scenarios

## Test Structure

### Test File Organization
```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_entities.py
│   │   └── test_value_objects.py
│   ├── application/
│   │   └── test_services.py
│   └── infrastructure/
│       └── test_repositories.py
├── integration/
│   ├── test_service_integration.py
│   └── test_event_integration.py
├── e2e/
│   └── test_workflows.py
└── data/
    ├── test_fixtures.json
    └── test_scenarios.json
```

### Test Naming Convention
```python
def test_[method_name]_[scenario]_[expected_outcome]():
    """
    Test that [method_name] [expected_outcome] when [scenario].
    """
```

Examples:
- `test_create_user_returns_success_when_valid_data()`
- `test_gain_experience_triggers_level_up_when_threshold_reached()`
- `test_validate_email_raises_error_when_invalid_format()`

## Test Data Management

### Test Fixtures
Location: `tests/data/`

#### Core Test Data
```json
{
  "valid_entities": [
    {
      "id": "test-entity-001",
      "field1": "valid_value",
      "field2": 42
    }
  ],
  "invalid_entities": [
    {
      "id": "",
      "field1": "invalid_value",
      "field2": -1
    }
  ]
}
```

#### Test Scenarios
```json
{
  "success_scenarios": [
    {
      "name": "successful_creation",
      "input": {...},
      "expected_output": {...}
    }
  ],
  "error_scenarios": [
    {
      "name": "validation_failure",
      "input": {...},
      "expected_error": "ValidationError"
    }
  ]
}
```

### Test Data Loading
```python
import json
import os

def load_test_data(filename: str) -> dict:
    """Load test data from JSON file."""
    test_data_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    with open(test_data_path, 'r') as f:
        return json.load(f)
```

## Unit Test Examples

### Domain Entity Tests
```python
def test_entity_creation_succeeds_with_valid_data():
    """Test that entity creation succeeds with valid data."""
    # Arrange
    valid_data = load_test_data('entities.json')['valid_entities'][0]
    
    # Act
    entity = EntityClass.create_new(
        field1=valid_data['field1'],
        field2=valid_data['field2']
    )
    
    # Assert
    assert entity.id is not None
    assert entity.field1 == valid_data['field1']
    assert entity.field2 == valid_data['field2']
    assert entity.created_at is not None

def test_entity_validation_fails_with_invalid_data():
    """Test that entity validation fails with invalid data."""
    # Arrange
    invalid_data = load_test_data('entities.json')['invalid_entities'][0]
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        EntityClass.create_new(
            field1=invalid_data['field1'],
            field2=invalid_data['field2']
        )
    
    assert "validation error message" in str(exc_info.value)
```

### Service Tests
```python
def test_service_method_returns_success_with_valid_request():
    """Test that service method returns success with valid request."""
    # Arrange
    repository = InMemoryRepository()
    service = ServiceClass(repository)
    request = CreateRequestDTO(field1="test", field2=42)
    
    # Act
    response = service.create(request)
    
    # Assert
    assert response.success is True
    assert response.resource_id is not None
    assert response.error is None

def test_service_method_returns_error_with_invalid_request():
    """Test that service method returns error with invalid request."""
    # Arrange
    repository = InMemoryRepository()
    service = ServiceClass(repository)
    request = CreateRequestDTO(field1="", field2=-1)
    
    # Act
    response = service.create(request)
    
    # Assert
    assert response.success is False
    assert response.resource_id is None
    assert response.error is not None
```

### Repository Tests
```python
def test_repository_save_persists_entity():
    """Test that repository save persists entity correctly."""
    # Arrange
    repository = InMemoryRepository()
    entity = EntityClass.create_new(field1="test", field2=42)
    
    # Act
    saved_entity = repository.save(entity)
    
    # Assert
    assert saved_entity.id == entity.id
    found_entity = repository.find_by_id(entity.id)
    assert found_entity is not None
    assert found_entity.field1 == entity.field1

def test_repository_find_by_id_returns_none_when_not_found():
    """Test that repository find_by_id returns None when entity not found."""
    # Arrange
    repository = InMemoryRepository()
    
    # Act
    found_entity = repository.find_by_id("non-existent-id")
    
    # Assert
    assert found_entity is None
```

## Integration Test Examples

### Service-Repository Integration
```python
def test_service_repository_integration():
    """Test complete service-repository integration."""
    # Arrange
    repository = InMemoryRepository()
    service = ServiceClass(repository)
    
    # Act - Create entity
    create_request = CreateRequestDTO(field1="test", field2=42)
    create_response = service.create(create_request)
    
    # Assert - Create succeeded
    assert create_response.success is True
    entity_id = create_response.resource_id
    
    # Act - Retrieve entity
    get_request = GetRequestDTO(id=entity_id)
    get_response = service.get_by_id(get_request)
    
    # Assert - Retrieve succeeded
    assert get_response.success is True
    assert get_response.data['field1'] == "test"
```

### Event Integration
```python
def test_event_publishing_integration():
    """Test that events are published correctly."""
    # Arrange
    event_store = InMemoryEventStore()
    repository = InMemoryRepository()
    service = ServiceClass(repository, event_publisher=event_store)
    
    # Act
    request = CreateRequestDTO(field1="test", field2=42)
    response = service.create(request)
    
    # Assert
    assert response.success is True
    published_events = event_store.get_published_events()
    assert len(published_events) == 1
    assert published_events[0].event_type == "EntityCreated"
```

## End-to-End Test Examples

### Complete Workflow Tests
```python
def test_complete_entity_lifecycle():
    """Test complete entity lifecycle from creation to deletion."""
    # Arrange
    service = setup_complete_service()
    
    # Act & Assert - Create
    create_request = CreateRequestDTO(field1="test", field2=42)
    create_response = service.create(create_request)
    assert create_response.success is True
    entity_id = create_response.resource_id
    
    # Act & Assert - Update
    update_request = UpdateRequestDTO(id=entity_id, updates={"field1": "updated"})
    update_response = service.update(update_request)
    assert update_response.success is True
    
    # Act & Assert - Delete
    delete_request = DeleteRequestDTO(id=entity_id)
    delete_response = service.delete(delete_request)
    assert delete_response.success is True
    
    # Act & Assert - Verify deletion
    get_request = GetRequestDTO(id=entity_id)
    get_response = service.get_by_id(get_request)
    assert get_response.success is False
```

## Test Scenarios

### Happy Path Scenarios
1. **Successful Creation**: Create entity with valid data
2. **Successful Update**: Update existing entity
3. **Successful Retrieval**: Get entity by ID
4. **Successful Deletion**: Delete existing entity

### Error Scenarios
1. **Validation Errors**: Invalid input data
2. **Not Found Errors**: Accessing non-existent entities
3. **Business Logic Errors**: Violating business rules
4. **Concurrency Errors**: Simultaneous access conflicts

### Edge Cases
1. **Boundary Values**: Minimum/maximum limits
2. **Empty Data**: Null or empty inputs
3. **Large Data**: Performance with large datasets
4. **Special Characters**: Unicode, special symbols

## Test Execution

### Running Tests

#### Manual Test Execution
```bash
# Run all tests
python3 manual_test.py

# Run specific test functions
python3 -c "from manual_test import test_specific_function; test_specific_function()"

# Run with debug output
export MODULE_DEBUG=true
python3 manual_test.py
```

#### Automated Test Execution (Future)
```bash
# Run with pytest (when available)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=module_name --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### Test Output Format
```
✅ test_create_entity_succeeds_with_valid_data: PASSED
✅ test_entity_validation_fails_with_invalid_data: PASSED
✅ test_service_integration_works_correctly: PASSED
❌ test_edge_case_handling: FAILED - AssertionError: Expected X, got Y

Test Summary:
- Total Tests: 15
- Passed: 14
- Failed: 1
- Success Rate: 93.3%
```

## Test Data Requirements

### Test Environment Setup
```python
def setup_test_environment():
    """Set up clean test environment for each test."""
    # Clear any existing data
    # Initialize repositories
    # Load test fixtures
    # Configure test settings
```

### Test Data Isolation
- Each test should use unique test data
- Tests should not depend on shared state
- Test data should be cleaned up after each test

### Test Data Versioning
- Version test data files with code changes
- Maintain backward compatibility when possible
- Document test data schema changes

## Performance Testing

### Performance Benchmarks
```python
def test_performance_create_entity():
    """Test that entity creation meets performance requirements."""
    import time
    
    # Arrange
    service = setup_service()
    request = CreateRequestDTO(field1="test", field2=42)
    
    # Act
    start_time = time.time()
    response = service.create(request)
    end_time = time.time()
    
    # Assert
    assert response.success is True
    assert (end_time - start_time) < 0.1  # Should complete in <100ms
```

### Load Testing
```python
def test_load_multiple_operations():
    """Test service performance under load."""
    service = setup_service()
    
    # Test creating multiple entities
    for i in range(100):
        request = CreateRequestDTO(field1=f"test_{i}", field2=i)
        response = service.create(request)
        assert response.success is True
```

## Test Coverage Requirements

### Coverage Targets
- **Unit Tests**: >90% code coverage
- **Integration Tests**: >80% integration path coverage
- **End-to-End Tests**: 100% critical path coverage

### Coverage Reporting
```bash
# Generate coverage report (future)
pytest --cov=module_name --cov-report=html --cov-report=term
```

### Uncovered Code Analysis
- Identify untested code paths
- Prioritize testing of critical functionality
- Document intentionally untested code (if any)

## Test Maintenance

### Regular Test Review
- Review tests for relevance and accuracy
- Update tests when business logic changes
- Remove obsolete or duplicate tests

### Test Refactoring
- Extract common test setup into fixtures
- Improve test readability and maintainability
- Optimize test execution time

### Test Documentation Updates
- Keep test documentation current with implementation
- Document new test scenarios and patterns
- Update test data when domain changes

## Troubleshooting

### Common Test Issues
1. **Import Errors**: Check Python path and module structure
2. **Test Data Issues**: Verify test data format and loading
3. **Assertion Failures**: Review expected vs. actual values
4. **Setup Problems**: Check test environment configuration

### Debug Strategies
```python
# Add debug prints to tests
def test_with_debugging():
    print("Debug: Starting test")
    # ... test code ...
    print(f"Debug: Response = {response}")
    # ... assertions ...
```

### Test Environment Validation
```bash
# Verify test environment
python3 -c "import sys; print(sys.path)"
python3 -c "from module_name import *; print('Imports successful')"
```

---

**Remember: Good tests are your safety net. They give you confidence to refactor, add features, and maintain code quality over time!**