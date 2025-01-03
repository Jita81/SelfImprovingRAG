# Self-Improving RAG System

A Retrieval-Augmented Generation (RAG) system that learns and improves from validation feedback.

## Overview

The Self-Improving RAG System is designed to enhance the quality and reliability of knowledge retrieval by continuously learning from validation results. It maintains a structured knowledge map and employs various mechanisms to validate, improve, and recover from validation issues.

## Core Components

### 1. Knowledge Map Management
- Maintains a graph-based representation of knowledge relationships
- Validates knowledge node connections and metadata
- Ensures consistency and quality of the knowledge base

### 2. Validation System
- Performs comprehensive validation of knowledge maps
- Checks for technical level consistency
- Validates prerequisites and learning paths
- Identifies potential bottlenecks and issues

### 3. Pattern Recognition System
- Analyzes validation history to identify recurring patterns
- Detects semantic similarities in validation issues
- Identifies temporal sequences of related issues
- Provides insights for system improvement
- [Learn more about Pattern Recognition](docs/pattern_recognition.md)

### 4. Recovery Management System
- Handles validation failures with automated recovery strategies
- Integrates with Pattern Recognition for intelligent recovery
- Manages concurrent recovery operations
- Tracks recovery history and effectiveness
- [Learn more about Recovery Management](docs/recovery_management.md)

### 5. Performance Monitoring System
- Tracks and analyzes system performance metrics
- Monitors validation success rates and confidence scores
- Measures recovery effectiveness and pattern detection
- Provides alerts for performance degradation
- [Learn more about Performance Monitoring](docs/performance_monitoring.md)

### 6. API Service
- Provides RESTful endpoints for system interaction
- Enables programmatic access to all components
- Supports validation, recovery, and monitoring
- Includes comprehensive error handling
- [Learn more about the API](docs/api.md)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/self-improving-rag.git
cd self-improving-rag
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the API server:
```bash
uvicorn src.api.api:app --reload
```

## Usage

### Python SDK
```python
from src.models.knowledge_map_validator import KnowledgeMapValidator
from src.services.pattern_recognition import PatternRecognitionService
from src.services.recovery_management import RecoveryManagementService
from src.services.performance_monitoring import PerformanceMonitoringService

# Initialize components
validator = KnowledgeMapValidator()
pattern_service = PatternRecognitionService(embedding_model)
recovery_service = RecoveryManagementService(pattern_service)
monitoring_service = PerformanceMonitoringService()

# Validate knowledge map
result = validator.validate_map(knowledge_map)

# Analyze validation patterns
patterns = pattern_service.analyze_validation_history(validation_results)

# Handle validation failures
if not result.is_valid:
    recovery_action = recovery_service.analyze_failure(result, validation_history)
    success = recovery_service.execute_recovery(
        recovery_action,
        {
            "knowledge_map": knowledge_map,
            "validation_system": validator
        }
    )

# Monitor performance
metrics = monitoring_service.calculate_metrics(
    validation_results=validation_history,
    detected_patterns=patterns,
    recovery_actions=recovery_service.recovery_history
)

# Check for alerts
alerts = monitoring_service.check_alerts(metrics)
```

### REST API
```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Validate knowledge map
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

## Testing

Run the test suite:
```bash
PYTHONPATH=$PYTHONPATH:. python3 -m pytest tests/ -v
```

## Documentation

- [System Architecture](docs/system-architecture.md)
- [Knowledge Map Validation](docs/knowledge-map-validation.md)
- [Pattern Recognition](docs/pattern_recognition.md)
- [Recovery Management](docs/recovery_management.md)
- [Performance Monitoring](docs/performance_monitoring.md)
- [API Documentation](docs/api.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 