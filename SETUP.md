# Self-Improving RAG System Setup

## Project Structure
```
SelfImprovingRAG/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── knowledge_validator.py
│   │   ├── test_generator.py
│   │   ├── knowledge_manager.py
│   │   └── rag_service.py
│   └── utils/
│       ├── __init__.py
│       └── embeddings.py
├── tests/
│   ├── __init__.py
│   ├── test_knowledge_validator.py
│   ├── test_test_generator.py
│   └── test_rag_service.py
└── docs/
    ├── refactor-stories.md
    └── api.md
```

## Setup Instructions

1. Clone the repository:
```bash
git clone git@github.com:Jita81/SelfImprovingRAG.git
cd SelfImprovingRAG
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
``` 