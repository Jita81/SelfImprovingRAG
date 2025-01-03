import pytest
from datetime import datetime
from src.models.domain import UseCaseDefinition, Document
from src.models.knowledge_map import KnowledgeMap, KnowledgeNode
from src.services.knowledge_generator import KnowledgeGenerator, GenerationStatus
from src.config import get_llm
import json
import asyncio

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
def simple_knowledge_map():
    nodes = [
        KnowledgeNode(
            id="1",
            topic="Basic Exceptions",
            description="Understanding basic exceptions in Python",
            required_prerequisites=[],
            validation_criteria=["Can explain what exceptions are"]
        ),
        KnowledgeNode(
            id="2",
            topic="Try-Except Blocks",
            description="Using try-except blocks for error handling",
            required_prerequisites=["1"],
            validation_criteria=["Can use try/except blocks"]
        )
    ]
    
    return KnowledgeMap(
        id="test",
        use_case_id="test-123",
        nodes=nodes
    )

@pytest.fixture
def generator():
    return KnowledgeGenerator(get_llm(), max_retries=3)

@pytest.mark.asyncio
async def test_single_node_generation(sample_use_case, simple_knowledge_map, generator):
    # Set longer timeout for basic content generation
    generator.set_timeout(45.0)
    
    try:
        # Generate content for the first node (no prerequisites)
        first_node = simple_knowledge_map.nodes[0]
        result = await asyncio.wait_for(
            generator.generate_content(first_node, simple_knowledge_map, sample_use_case),
            timeout=50.0  # Overall test timeout
        )
        
        # Check generation result
        assert result.success, f"Generation failed: {result.issues}"
        assert result.document is not None
        assert len(result.document.content) > 0
        assert "exception" in result.document.content.lower()
        assert result.document.metadata["node_id"] == first_node.id
        assert len(result.document.metadata["examples"]) > 0
        assert len(result.document.metadata["validation_points"]) > 0
        assert result.retry_count <= 2, "Should succeed within 3 attempts"  # Allow some retries
        assert result.document.confidence_score > 0, "Should have positive confidence"
    except asyncio.TimeoutError:
        pytest.fail("Test timed out")

@pytest.mark.asyncio
async def test_dependent_node_generation(sample_use_case, simple_knowledge_map, generator):
    # Set appropriate timeout for dependent content
    generator.set_timeout(30.0)
    
    try:
        # First generate the prerequisite content
        first_node = simple_knowledge_map.nodes[0]
        prereq_result = await asyncio.wait_for(
            generator.generate_content(first_node, simple_knowledge_map, sample_use_case),
            timeout=35.0
        )
        assert prereq_result.success
        
        # Then generate content for the dependent node
        second_node = simple_knowledge_map.nodes[1]
        result = await asyncio.wait_for(
            generator.generate_content(
                second_node, 
                simple_knowledge_map,
                sample_use_case,
                [prereq_result.document]
            ),
            timeout=35.0
        )
        
        # Check generation result
        assert result.success, f"Generation failed: {result.issues}"
        assert result.document is not None
        assert len(result.document.content) > 0
        assert "try" in result.document.content.lower()
        assert "except" in result.document.content.lower()
        assert result.document.metadata["node_id"] == second_node.id
        assert len(result.document.metadata["examples"]) > 0
        assert len(result.document.metadata["validation_points"]) > 0
    except asyncio.TimeoutError:
        pytest.fail("Test timed out")

@pytest.mark.asyncio
async def test_generate_all(sample_use_case, simple_knowledge_map, generator):
    # Set appropriate timeout for all content generation
    generator.set_timeout(30.0)
    
    try:
        # Generate all content with overall timeout
        results = await asyncio.wait_for(
            generator.generate_all(simple_knowledge_map, sample_use_case),
            timeout=70.0  # Allow time for both nodes
        )
        
        # Check results
        assert len(results) == len(simple_knowledge_map.nodes)
        assert all(r.success for r in results)
        
        # Check content order and dependencies
        documents = [r.document for r in results]
        assert documents[0].metadata["node_id"] == "1"  # Basic Exceptions should be first
        assert documents[1].metadata["node_id"] == "2"  # Try-Except should be second
        
        # Check that second document references first
        assert any("exception" in ref.lower() 
                  for ref in documents[1].metadata["references"])
    except asyncio.TimeoutError:
        pytest.fail("Test timed out")

@pytest.mark.asyncio
async def test_retry_behavior(sample_use_case, generator):
    # Set short timeout to trigger retries
    generator.set_timeout(5.0)
    
    # Create a node with validation criteria that should trigger retries
    node = KnowledgeNode(
        id="test",
        topic="Complex Error Handling",
        description="Advanced error handling patterns",
        required_prerequisites=[],
        validation_criteria=[
            "Must explain error handling patterns in detail",
            "Must include at least 5 examples with code",
            "Must cover edge cases",
            "Must include performance considerations",
            "Must provide implementation guidelines"
        ]
    )
    
    knowledge_map = KnowledgeMap(
        id="test",
        use_case_id=sample_use_case.id,
        nodes=[node]
    )
    
    try:
        # Generate content - should require multiple attempts and ultimately fail
        result = await asyncio.wait_for(
            generator.generate_content(node, knowledge_map, sample_use_case),
            timeout=20.0  # Allow time for all retries
        )
        
        # Check retry behavior
        assert not result.success, "Should fail due to complex requirements"
        assert result.retry_count == generator.max_retries, "Should attempt maximum number of retries"
        assert result.document is None, "Should not return a document on failure"
        assert len(result.issues) > 0, "Should report specific issues"
        
        # With short timeout, we expect timeout issues
        issues_text = " ".join(result.issues).lower()
        assert any(word in issues_text for word in ["timeout", "timed out"]), "Should mention timeout issues"
    except asyncio.TimeoutError:
        pytest.fail("Test timed out")

@pytest.mark.asyncio
async def test_missing_prerequisites(sample_use_case, simple_knowledge_map, generator):
    try:
        # Try to generate content for the second node without prerequisites
        second_node = simple_knowledge_map.nodes[1]
        result = await asyncio.wait_for(
            generator.generate_content(second_node, simple_knowledge_map, sample_use_case),
            timeout=10.0
        )
        
        # Check failure handling
        assert not result.success
        assert "Missing prerequisite" in result.issues[0]
        assert result.document is None
    except asyncio.TimeoutError:
        pytest.fail("Test timed out") 