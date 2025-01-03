# API Documentation

The Self-Improving RAG System provides a RESTful API for interacting with all system components. The API enables validation, pattern recognition, recovery management, and performance monitoring.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production use, appropriate authentication mechanisms should be implemented.

## Endpoints

### Health Check

```http
GET /health
```

Returns the API health status.

**Response**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Knowledge Map Validation

```http
POST /validate
```

Validates a knowledge map structure.

**Request Body**
```json
{
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
```

**Response**
```json
{
    "is_valid": true,
    "issues": [],
    "confidence_score": 0.95,
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Pattern Recognition

```http
GET /patterns?min_significance=0.5
```

Retrieves detected patterns with minimum significance.

**Parameters**
- `min_significance` (float, optional): Minimum pattern significance threshold (default: 0.5)

**Response**
```json
[
    {
        "pattern_type": "semantic",
        "description": "Technical level inconsistencies",
        "significance": 0.8,
        "occurrences": 3,
        "first_seen": "2024-01-01T10:00:00.000Z",
        "last_seen": "2024-01-01T12:00:00.000Z",
        "related_issues": ["Technical level mismatch"],
        "metadata": {
            "cluster_size": 2,
            "average_similarity": 0.85
        }
    }
]
```

### Recovery Management

```http
POST /recover
```

Executes recovery action for validation failure.

**Request Body**
```json
{
    "validation_result": {
        "is_valid": false,
        "issues": ["Technical level mismatch"],
        "confidence_score": 0.8,
        "timestamp": "2024-01-01T12:00:00.000Z"
    },
    "knowledge_map": {
        "nodes": {},
        "edges": []
    }
}
```

**Response**
```json
true
```

### Performance Metrics

```http
GET /metrics?window_size=24
```

Retrieves current performance metrics.

**Parameters**
- `window_size` (int, optional): Time window in hours (default: 24)

**Response**
```json
{
    "validation_success_rate": 0.85,
    "recovery_success_rate": 0.75,
    "pattern_detection_rate": 0.6,
    "average_confidence_score": 0.9,
    "critical_failure_rate": 0.1,
    "recovery_time": 180,
    "window_size": 86400,
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Performance Alerts

```http
GET /alerts
```

Retrieves current performance alerts.

**Response**
```json
[
    {
        "metric_type": "validation_success_rate",
        "current_value": 0.75,
        "threshold": 0.8,
        "timestamp": "2024-01-01T12:00:00.000Z",
        "metadata": {
            "total_validations": 100,
            "successful_validations": 75
        }
    }
]
```

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `422`: Validation Error (invalid request body)
- `500`: Internal Server Error

Error Response Format:
```json
{
    "detail": "Error message describing the issue"
}
```

## Data Models

### KnowledgeMap
```python
{
    "nodes": Dict[str, Dict[str, Any]],
    "edges": List[Dict[str, Any]]
}
```

### ValidationResult
```python
{
    "is_valid": bool,
    "issues": List[str],
    "confidence_score": float,
    "timestamp": datetime
}
```

### Pattern
```python
{
    "pattern_type": str,
    "description": str,
    "significance": float,
    "occurrences": int,
    "first_seen": datetime,
    "last_seen": datetime,
    "related_issues": List[str],
    "metadata": Dict[str, Any]
}
```

### PerformanceMetrics
```python
{
    "validation_success_rate": Optional[float],
    "recovery_success_rate": Optional[float],
    "pattern_detection_rate": Optional[float],
    "average_confidence_score": Optional[float],
    "critical_failure_rate": Optional[float],
    "recovery_time": Optional[float],
    "window_size": timedelta,
    "timestamp": datetime
}
```

### Alert
```python
{
    "metric_type": str,
    "current_value": float,
    "threshold": float,
    "timestamp": datetime,
    "metadata": Dict[str, Any]
}
```

## Usage Examples

### Python
```python
import requests
import json

# Base URL
base_url = "http://localhost:8000"

# Validate knowledge map
knowledge_map = {
    "nodes": {...},
    "edges": [...]
}
response = requests.post(f"{base_url}/validate", json=knowledge_map)
validation_result = response.json()

# Get patterns
response = requests.get(f"{base_url}/patterns", params={"min_significance": 0.7})
patterns = response.json()

# Execute recovery
recovery_request = {
    "validation_result": validation_result,
    "knowledge_map": knowledge_map
}
response = requests.post(f"{base_url}/recover", json=recovery_request)
success = response.json()

# Get metrics
response = requests.get(f"{base_url}/metrics", params={"window_size": 48})
metrics = response.json()

# Get alerts
response = requests.get(f"{base_url}/alerts")
alerts = response.json()
```

### cURL
```bash
# Health check
curl http://localhost:8000/health

# Validate knowledge map
curl -X POST http://localhost:8000/validate \
    -H "Content-Type: application/json" \
    -d @knowledge_map.json

# Get patterns
curl http://localhost:8000/patterns?min_significance=0.7

# Execute recovery
curl -X POST http://localhost:8000/recover \
    -H "Content-Type: application/json" \
    -d @recovery_request.json

# Get metrics
curl http://localhost:8000/metrics?window_size=48

# Get alerts
curl http://localhost:8000/alerts
```

## Future Improvements

1. **Authentication & Authorization**:
   - Add API key authentication
   - Implement role-based access control
   - Add rate limiting

2. **Enhanced Functionality**:
   - Batch validation endpoint
   - Async recovery operations
   - WebSocket support for real-time updates

3. **Documentation**:
   - Interactive API documentation (Swagger/OpenAPI)
   - Code examples in multiple languages
   - Integration guides 