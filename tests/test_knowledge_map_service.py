import pytest
from datetime import datetime
from src.models.domain import UseCaseDefinition
from src.models.knowledge_map import KnowledgeMap, KnowledgeNode
from src.services.knowledge_map_service import KnowledgeMapService
from src.config import get_llm

@pytest.fixture
def sample_use_case():
    return UseCaseDefinition(
        id="test-123",
        name="Python Error Handling",
        description="Understanding and implementing error handling in Python",
        domain="Python Programming",
        technical_level="intermediate",
        success_criteria=["Can explain try/except", "Can handle multiple exceptions"],
        output_requirements={
            "format": "text",
            "structure": {"type": "explanation"},
            "validation_rules": ["Must include examples"],
            "examples": [{"query": "How to handle errors?", "response": "Use try/except..."}]
        },
        knowledge_prerequisites=[],
        example_queries=[]
    )

@pytest.fixture
def knowledge_map_service():
    return KnowledgeMapService(get_llm())

@pytest.mark.asyncio
async def test_knowledge_map_generation(sample_use_case, knowledge_map_service):
    # Generate knowledge map
    knowledge_map = await knowledge_map_service.generate_map(sample_use_case)
    
    # Basic structure tests
    assert isinstance(knowledge_map, KnowledgeMap)
    assert knowledge_map.use_case_id == sample_use_case.id
    assert len(knowledge_map.nodes) > 0
    
    # Content tests
    for node in knowledge_map.nodes:
        assert isinstance(node, KnowledgeNode)
        assert node.topic, "Node must have a topic"
        assert len(node.topic) > 0, "Topic cannot be empty"
        assert node.description, "Node must have a description"
        assert len(node.description) > 0, "Description cannot be empty"
        assert isinstance(node.validation_criteria, list), "Validation criteria must be a list"
        assert len(node.validation_criteria) > 0, "Must have at least one validation criterion"
        
    # Dependency validation
    sequence = knowledge_map.get_generation_sequence()
    assert len(sequence) == len(knowledge_map.nodes), "Sequence must contain all nodes"
    
    # Check for circular dependencies
    seen_nodes = set()
    for node in sequence:
        assert all(prereq in seen_nodes for prereq in node.required_prerequisites), \
            "All prerequisites must appear before dependent nodes"
        seen_nodes.add(node.id)
    
    # Check for Python error handling specific content
    topics = {node.topic.lower() for node in knowledge_map.nodes}
    expected_topics = {"try/except", "exceptions", "error handling"}
    assert any(any(expected in topic for expected in expected_topics) for topic in topics), \
        "Knowledge map should contain topics related to error handling" 