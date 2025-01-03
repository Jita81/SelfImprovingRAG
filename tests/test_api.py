import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from typing import Dict, Any

from src.api.api import app
from src.models.validation_result import ValidationResult
from src.services.pattern_recognition import Pattern

client = TestClient(app)

@pytest.fixture
def sample_knowledge_map() -> Dict[str, Any]:
    return {
        "nodes": {
            "node1": {
                "id": "node1",
                "title": "Introduction to Python",
                "description": "Basic Python programming concepts",
                "technical_level": 1
            },
            "node2": {
                "id": "node2",
                "title": "Advanced Python",
                "description": "Advanced Python programming concepts",
                "technical_level": 2,
                "prerequisites": ["node1"]
            }
        },
        "edges": [
            {
                "source": "node1",
                "target": "node2",
                "type": "prerequisite"
            }
        ]
    }

@pytest.fixture
def sample_validation_result() -> Dict[str, Any]:
    return {
        "is_valid": False,
        "issues": ["Technical level mismatch"],
        "confidence_score": 0.8,
        "timestamp": datetime.now().isoformat()
    }

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_validate_knowledge_map(sample_knowledge_map):
    """Test knowledge map validation endpoint"""
    response = client.post("/validate", json=sample_knowledge_map)
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data
    assert "issues" in data
    assert "confidence_score" in data
    assert "timestamp" in data

def test_validate_invalid_knowledge_map():
    """Test validation with invalid knowledge map"""
    invalid_map = {
        "nodes": {},
        "edges": [{"invalid": "edge"}]
    }
    response = client.post("/validate", json=invalid_map)
    assert response.status_code == 200
    data = response.json()
    assert not data["is_valid"]
    assert len(data["issues"]) > 0

def test_get_patterns():
    """Test pattern retrieval endpoint"""
    response = client.get("/patterns?min_significance=0.5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If patterns exist
        pattern = data[0]
        assert "pattern_type" in pattern
        assert "description" in pattern
        assert "significance" in pattern
        assert "occurrences" in pattern

def test_get_patterns_high_significance():
    """Test pattern retrieval with high significance threshold"""
    response = client.get("/patterns?min_significance=0.9")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for pattern in data:
        assert pattern["significance"] >= 0.9

def test_execute_recovery(sample_validation_result, sample_knowledge_map):
    """Test recovery execution endpoint"""
    response = client.post(
        "/recover",
        json={
            "validation_result": sample_validation_result,
            "knowledge_map": sample_knowledge_map
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), bool)

def test_execute_recovery_valid_result(sample_knowledge_map):
    """Test recovery execution with valid result"""
    valid_result = {
        "is_valid": True,
        "issues": [],
        "confidence_score": 1.0,
        "timestamp": datetime.now().isoformat()
    }
    response = client.post(
        "/recover",
        json={
            "validation_result": valid_result,
            "knowledge_map": sample_knowledge_map
        }
    )
    assert response.status_code == 400
    assert "Cannot recover from valid result" in response.json()["detail"]

def test_get_metrics():
    """Test metrics retrieval endpoint"""
    response = client.get("/metrics?window_size=24")
    assert response.status_code == 200
    data = response.json()
    assert "validation_success_rate" in data
    assert "recovery_success_rate" in data
    assert "pattern_detection_rate" in data
    assert "average_confidence_score" in data
    assert "critical_failure_rate" in data
    assert "recovery_time" in data
    assert "window_size" in data
    assert "timestamp" in data

def test_get_metrics_custom_window():
    """Test metrics retrieval with custom window size"""
    response = client.get("/metrics?window_size=48")
    assert response.status_code == 200
    data = response.json()
    assert data["window_size"] == 172800  # 48 hours in seconds

def test_get_alerts():
    """Test alerts retrieval endpoint"""
    response = client.get("/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If alerts exist
        alert = data[0]
        assert "metric_type" in alert
        assert "current_value" in alert
        assert "threshold" in alert
        assert "timestamp" in alert
        assert "metadata" in alert

def test_api_error_handling():
    """Test API error handling"""
    # Test invalid JSON
    response = client.post("/validate", json="invalid")
    assert response.status_code == 422
    
    # Test missing required fields
    response = client.post("/validate", json={})
    assert response.status_code == 422
    
    # Test invalid query parameter
    response = client.get("/metrics?window_size=invalid")
    assert response.status_code == 422 