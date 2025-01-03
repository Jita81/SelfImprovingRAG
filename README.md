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

### Creating a Use Case

```bash
curl -X POST http://localhost:8001/use-cases/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Use Case",
    "description": "Description of the use case",
    "domain": "example_domain",
    "technical_level": "intermediate",
    "success_criteria": ["Criteria 1", "Criteria 2"],
    "acceptance_criteria": ["Acceptance 1", "Acceptance 2"]
  }'
```

### Querying the System

```bash
curl -X POST http://localhost:8001/queries/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your question here",
    "use_case": "Example Use Case",
    "domain": "example_domain"
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