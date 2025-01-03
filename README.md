# Self-Improving RAG System

A sophisticated Retrieval-Augmented Generation (RAG) system that continuously improves its knowledge base through automated learning and validation.

## Overview

The Self-Improving RAG System is designed to maintain and enhance a dynamic knowledge base by:
- Processing and validating new use cases
- Detecting patterns in validation issues
- Automatically improving its knowledge base
- Monitoring performance metrics
- Implementing recovery strategies for failures

## Key Features

- **Knowledge Map Generation**: Automatically creates and maintains structured knowledge maps from use cases
- **Continuous Validation**: Validates knowledge against defined criteria and test cases
- **Pattern Recognition**: Identifies patterns in validation issues to guide improvements
- **Self-Improvement**: Automatically enhances knowledge base based on detected patterns
- **Performance Monitoring**: Tracks system health and effectiveness metrics
- **Recovery Management**: Handles failures and implements recovery strategies
- **API Integration**: RESTful API for easy integration with other systems

## Documentation

### Core Components
- [Knowledge Map System](docs/knowledge_map_system.md): Core knowledge representation and management
- [LLM Integration](docs/llm_integration.md): Integration with Large Language Models
- [Knowledge Validation](docs/knowledge_validation.md): Validation process and criteria
- [Use Case Management](docs/use_case_management.md): Use case processing and management

### System Features
- [Pattern Recognition](docs/pattern_recognition.md): Pattern detection and analysis
- [Performance Monitoring](docs/performance_monitoring.md): System metrics and monitoring
- [Recovery Management](docs/recovery_management.md): Failure handling and recovery
- [API Reference](docs/api.md): Complete API documentation

## Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key
- FastAPI
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/self-improving-rag.git
cd self-improving-rag
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

5. Start the server:
```bash
python run_api.py
```

## Usage

The system provides three main endpoints for interaction:

### 1. Creating a Use Case

Create a new use case to define a knowledge domain:

```bash
curl -X POST http://localhost:8001/use-cases/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Epic Feature Breakdown",
    "description": "A system that analyzes Azure DevOps epic descriptions and breaks them down into modular, well-defined features.",
    "domain": "feature_breakdown",
    "technical_level": "intermediate",
    "success_criteria": [
      "Identify all core functionalities from epic description",
      "Create modular and independent features",
      "Ensure complete coverage of epic requirements"
    ],
    "acceptance_criteria": [
      "Each feature should be independently implementable",
      "All epic requirements must be covered",
      "Dependencies between features must be clearly identified"
    ],
    "output_requirements": {
      "format": "text",
      "structure": {"type": "explanation"},
      "validation_rules": ["Must be clear and actionable"],
      "examples": []
    },
    "knowledge_prerequisites": [
      "Understanding of SOLID principles",
      "Knowledge of modular design"
    ],
    "example_queries": [
      "How to handle cross-cutting concerns?",
      "What is the optimal feature size?"
    ]
  }'
```

### 2. Querying the System

Query the system with specific questions or scenarios:

```bash
curl -X POST http://localhost:8001/queries/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How should I break down this epic: \"Implement a secure document management system with version control, access control, and full-text search capabilities\"",
    "use_case": "Epic Feature Breakdown",
    "domain": "feature_breakdown"
  }'
```

### 3. Reporting Bugs/Improvements

Report issues or suggest improvements to help the system learn:

```bash
curl -X POST http://localhost:8001/bugs/ \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "Epic Feature Breakdown",
    "domain": "feature_breakdown",
    "description": "System does not properly handle cross-cutting concerns in feature breakdown",
    "steps_to_reproduce": [
      "Create an epic with security requirements that affect multiple features",
      "Request feature breakdown",
      "Observe that security requirements are duplicated across features"
    ],
    "expected_behavior": "System should identify cross-cutting concerns and suggest them as separate architectural features or aspects",
    "actual_behavior": "System duplicates cross-cutting concerns across multiple features"
  }'
```

## Architecture

The system follows a modular architecture with these key components:

- **API Layer**: FastAPI-based REST API
- **Service Layer**: Core business logic and processing
- **Model Layer**: Data models and validation
- **Storage Layer**: Knowledge base and metadata storage

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT models
- FastAPI framework
- All contributors and maintainers 