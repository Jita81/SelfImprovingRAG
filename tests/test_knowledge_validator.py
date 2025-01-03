import pytest
import os
from unittest.mock import patch, MagicMock
from src.services.knowledge_validator import KnowledgeValidator
from src.models.use_case import UseCase
from src.models.validation_result import ValidationResult

@pytest.fixture
def mock_openai_response():
    return {
        "technical_level_appropriate": True,
        "criteria_coverage": {
            "Can explain try/except blocks": "covered",
            "Can handle multiple exceptions": "covered",
            "Can use context managers": "covered"
        },
        "improvement_suggestions": []
    }

@pytest.fixture
def mock_openai_response_incomplete():
    return {
        "technical_level_appropriate": True,
        "criteria_coverage": {
            "Can explain try/except blocks": "partial",
            "Can handle multiple exceptions": "not_covered",
            "Can use context managers": "not_covered"
        },
        "improvement_suggestions": [
            "Add examples of handling multiple exceptions",
            "Explain context managers in more detail"
        ]
    }

@pytest.fixture
def mock_openai_response_expert():
    return {
        "technical_level_appropriate": False,
        "criteria_coverage": {
            "Can explain try/except blocks": "covered",
            "Can handle multiple exceptions": "covered",
            "Can use context managers": "covered"
        },
        "improvement_suggestions": [
            "Add more advanced error handling patterns",
            "Discuss internal implementation details"
        ]
    }

@pytest.fixture
def validator():
    os.environ["OPENAI_API_KEY"] = "sk-mock-key"  # Mock API key for testing
    return KnowledgeValidator(
        model_name="gpt-3.5-turbo",
        timeout=30
    )

@pytest.fixture
def good_document():
    return """Python error handling is implemented using try/except blocks. Here's how they work:

When an exception occurs, Python looks for a matching except block to handle it. If no matching except block is found, the exception propagates up the call stack until it's caught or crashes the program.

Context managers (using 'with' statements) provide automatic resource cleanup. They ensure that resources like files are properly closed even if an error occurs. The context manager protocol (__enter__ and __exit__ methods) handles setup and cleanup automatically.

You can handle multiple exceptions by having multiple except blocks:

try:
    file = open('data.txt')
    data = file.read()
except FileNotFoundError:
    print('File not found')
except PermissionError:
    print('Permission denied')
finally:
    file.close()

This pattern ensures resources are properly managed even if errors occur."""

@pytest.fixture
def incomplete_document():
    return """Python has error handling. You can use try/except blocks.
Sometimes errors happen when reading files."""

@pytest.fixture
def use_case():
    return UseCase(
        name="Python Error Handling",
        description="Understanding Python's error handling mechanisms",
        technical_level="intermediate",
        success_criteria=[
            "Can explain try/except blocks",
            "Can handle multiple exceptions",
            "Can use context managers"
        ],
        dependencies=[]
    )

@patch('langchain_openai.ChatOpenAI')
def test_validate_good_content(mock_chat, validator, good_document, use_case, mock_openai_response):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_openai_response
    validator.chain = mock_chain
    
    result = validator.validate_content(good_document, use_case)
    assert result.is_valid, f"Content should be valid. Issues: {result.issues}"
    assert result.confidence_score == 1.0, "Should have perfect confidence score for valid content"
    assert result.timestamp is not None, "Should have timestamp"

@patch('langchain_openai.ChatOpenAI')
def test_validate_incomplete_content(mock_chat, validator, incomplete_document, use_case, mock_openai_response_incomplete):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_openai_response_incomplete
    validator.chain = mock_chain
    
    result = validator.validate_content(incomplete_document, use_case)
    assert not result.is_valid, "Content should be invalid"
    assert len(result.issues) > 0, "Should have issues"
    assert 0 < result.confidence_score < 0.5, "Should have low confidence score for incomplete content"
    assert result.timestamp is not None, "Should have timestamp"

@patch('langchain_openai.ChatOpenAI')
def test_validation_timeout(mock_chat, validator, good_document, use_case):
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = TimeoutError("Request timed out")
    validator.chain = mock_chain
    
    result = validator.validate_content(good_document, use_case)
    assert not result.is_valid
    assert result.issues[0] == "Validation timed out"
    assert result.confidence_score == 0.0, "Should have zero confidence for timeout"
    assert result.timestamp is not None, "Should have timestamp"

@patch('langchain_openai.ChatOpenAI')
def test_technical_level_validation(mock_chat, validator, good_document, use_case, mock_openai_response_expert):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_openai_response_expert
    validator.chain = mock_chain
    
    use_case.technical_level = "expert"
    result = validator.validate_content(good_document, use_case)
    assert not result.is_valid
    assert "technical level" in result.issues[0].lower()
    assert 0.4 <= result.confidence_score <= 0.5, "Should have significantly reduced confidence for technical level mismatch"
    assert result.timestamp is not None, "Should have timestamp"

def test_validation_history_tracking(validator, use_case, good_document, mock_openai_response):
    """Test that validation results are tracked in history"""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_openai_response
    validator.chain = mock_chain
    
    # First validation
    result1 = validator.validate_content(good_document, use_case)
    assert len(validator.history.history) == 1
    assert validator.history.history[0] == result1
    
    # Second validation with different response
    mock_chain.invoke.return_value = mock_openai_response_incomplete
    result2 = validator.validate_content(incomplete_document, use_case)
    assert len(validator.history.history) == 2
    assert validator.history.history[1] == result2

def test_validation_trends(validator, use_case, good_document, mock_openai_response, mock_openai_response_incomplete):
    """Test getting validation trends"""
    mock_chain = MagicMock()
    
    # First validation - good content
    mock_chain.invoke.return_value = mock_openai_response
    validator.chain = mock_chain
    validator.validate_content(good_document, use_case)
    
    # Second validation - incomplete content
    mock_chain.invoke.return_value = mock_openai_response_incomplete
    validator.validate_content(good_document, use_case)
    
    trends = validator.get_validation_trends()
    assert "average_confidence" in trends
    assert "common_issues" in trends
    assert len(trends["common_issues"]) > 0  # Should have some common issues
    assert 0 <= trends["average_confidence"] <= 1.0  # Should have valid confidence score

def test_error_tracking(validator, use_case, good_document):
    """Test that errors are tracked in validation history"""
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = TimeoutError("Request timed out")
    validator.chain = mock_chain
    
    result = validator.validate_content(good_document, use_case)
    assert len(validator.history.history) == 1
    assert validator.history.history[0] == result
    assert result.issues[0] == "Validation timed out"
    
    trends = validator.get_validation_trends()
    assert trends["average_confidence"] == 0.0  # Timeout should result in zero confidence 