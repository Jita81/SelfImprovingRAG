import pytest
from datetime import datetime
from src.models.knowledge_map_validator import KnowledgeMapValidator

@pytest.fixture
def validator():
    return KnowledgeMapValidator()

@pytest.fixture
def valid_nodes():
    return [
        {
            "id": "1",
            "topic": "Basic Concepts",
            "description": "A comprehensive introduction to the basic concepts of the subject matter. This includes fundamental principles and key terminology.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "2",
            "topic": "Intermediate Topics",
            "description": "Building upon the basic concepts, this section covers intermediate level topics and practical applications. Students will learn more advanced techniques.",
            "required_prerequisites": ["1"],
            "technical_level": "intermediate"
        },
        {
            "id": "3",
            "topic": "Advanced Topics",
            "description": "Advanced concepts and techniques are covered in this section. Students will learn complex problem-solving approaches and specialized methodologies.",
            "required_prerequisites": ["1", "2"],
            "technical_level": "advanced"
        }
    ]

def test_empty_map(validator):
    """Test validation of empty knowledge map"""
    result = validator.validate_map([])
    assert not result.is_valid
    assert "Empty knowledge map" in result.issues
    assert result.confidence_score == 1.0

def test_valid_map(validator, valid_nodes):
    """Test validation of valid knowledge map"""
    result = validator.validate_map(valid_nodes)
    assert result.is_valid
    assert not result.issues
    assert result.confidence_score == 1.0

def test_duplicate_ids(validator, valid_nodes):
    """Test detection of duplicate node IDs"""
    # Add duplicate node
    duplicate_nodes = valid_nodes + [{
        "id": "1",  # Duplicate ID
        "topic": "Another Topic",
        "description": "Another comprehensive description of the topic that meets the minimum length requirement.",
        "required_prerequisites": [],
        "technical_level": "beginner"
    }]
    
    result = validator.validate_map(duplicate_nodes)
    assert not result.is_valid
    assert "Duplicate node IDs found" in result.issues
    assert result.confidence_score < 1.0

def test_missing_fields(validator):
    """Test detection of missing required fields"""
    incomplete_nodes = [{
        "id": "1",
        "topic": "Basic Concepts"
        # Missing description, required_prerequisites, and technical_level
    }]
    
    result = validator.validate_map(incomplete_nodes)
    assert not result.is_valid
    assert any("missing required fields" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_undefined_prerequisites(validator, valid_nodes):
    """Test detection of undefined prerequisites"""
    # Add node with undefined prerequisite
    nodes_with_undefined = valid_nodes + [{
        "id": "4",
        "topic": "New Topic",
        "description": "A comprehensive description of the new topic that meets the minimum length requirement.",
        "required_prerequisites": ["5"],  # Undefined prerequisite
        "technical_level": "intermediate"
    }]
    
    result = validator.validate_map(nodes_with_undefined)
    assert not result.is_valid
    assert any("undefined prerequisites" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_circular_dependencies(validator):
    """Test detection of circular dependencies"""
    circular_nodes = [
        {
            "id": "1",
            "topic": "Topic A",
            "description": "A comprehensive description of Topic A that meets the minimum length requirement.",
            "required_prerequisites": ["2"],
            "technical_level": "beginner"
        },
        {
            "id": "2",
            "topic": "Topic B",
            "description": "A comprehensive description of Topic B that meets the minimum length requirement.",
            "required_prerequisites": ["3"],
            "technical_level": "intermediate"
        },
        {
            "id": "3",
            "topic": "Topic C",
            "description": "A comprehensive description of Topic C that meets the minimum length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "advanced"
        }
    ]
    
    result = validator.validate_map(circular_nodes)
    assert not result.is_valid
    assert "Circular dependencies detected" in result.issues
    assert result.confidence_score < 1.0

def test_complex_valid_dependencies(validator):
    """Test validation of complex but valid dependency structure"""
    complex_nodes = [
        {
            "id": "1",
            "topic": "Basics",
            "description": "A comprehensive introduction to the basic concepts that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "2",
            "topic": "Intermediate",
            "description": "Building upon the basics with intermediate concepts and applications that meets the length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "intermediate"
        },
        {
            "id": "3",
            "topic": "Advanced A",
            "description": "Advanced concepts and techniques for track A that meets the minimum length requirement.",
            "required_prerequisites": ["1", "2"],
            "technical_level": "advanced"
        },
        {
            "id": "4",
            "topic": "Advanced B",
            "description": "Advanced concepts and techniques for track B that meets the minimum length requirement.",
            "required_prerequisites": ["1", "2"],
            "technical_level": "advanced"
        },
        {
            "id": "5",
            "topic": "Expert",
            "description": "Expert level concepts and techniques that build upon both advanced tracks A and B.",
            "required_prerequisites": ["3", "4"],
            "technical_level": "expert"
        }
    ]
    
    result = validator.validate_map(complex_nodes)
    assert result.is_valid
    assert not result.issues
    assert result.confidence_score == 1.0

def test_multiple_issues(validator):
    """Test handling of multiple validation issues"""
    problematic_nodes = [
        {
            "id": "1",
            "topic": "Topic A",
            # Missing description and technical_level
            "required_prerequisites": ["2"]
        },
        {
            "id": "1",  # Duplicate ID
            "topic": "Topic B",
            "description": "Short",  # Too short
            "required_prerequisites": ["3"],  # Undefined prerequisite
            "technical_level": "invalid"  # Invalid level
        }
    ]
    
    result = validator.validate_map(problematic_nodes)
    assert not result.is_valid
    assert len(result.issues) >= 5  # Should find multiple issues
    assert result.confidence_score < 0.5  # Confidence should be low with multiple issues

def test_description_length(validator):
    """Test validation of description length"""
    nodes = [
        {
            "id": "1",
            "topic": "Short Description",
            "description": "Too short",  # Less than min_description_length
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "2",
            "topic": "Long Description",
            "description": "x" * 1001,  # Exceeds max_description_length
            "required_prerequisites": [],
            "technical_level": "beginner"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("description too short" in issue for issue in result.issues)
    assert any("description too long" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_technical_level_validation(validator):
    """Test validation of technical levels"""
    nodes = [
        {
            "id": "1",
            "topic": "Invalid Level",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "invalid_level"
        },
        {
            "id": "2",
            "topic": "Advanced Before Beginner",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["3"],
            "technical_level": "beginner"
        },
        {
            "id": "3",
            "topic": "Prerequisite",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "advanced"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("invalid technical level" in issue for issue in result.issues)
    assert any("higher technical level" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_isolated_nodes(validator):
    """Test detection of isolated nodes"""
    nodes = [
        {
            "id": "1",
            "topic": "Connected Node",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "2",
            "topic": "Isolated Node",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "3",
            "topic": "Dependent Node",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "intermediate"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("is isolated" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_long_learning_path(validator):
    """Test detection of overly long learning paths"""
    # Create a chain of 11 nodes (exceeding max_path_length of 10)
    nodes = []
    for i in range(11):
        nodes.append({
            "id": str(i + 1),
            "topic": f"Topic {i + 1}",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [] if i == 0 else [str(i)],
            "technical_level": "beginner"
        })
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("Learning path" in issue and "too long" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_non_progressive_learning_path(validator):
    """Test detection of non-progressive technical levels in learning paths"""
    nodes = [
        {
            "id": "1",
            "topic": "Advanced First",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "advanced"
        },
        {
            "id": "2",
            "topic": "Beginner Second",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "beginner"
        },
        {
            "id": "3",
            "topic": "Expert Last",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["2"],
            "technical_level": "expert"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("Non-progressive technical levels" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_multiple_valid_paths(validator):
    """Test validation of multiple valid learning paths"""
    nodes = [
        {
            "id": "1",
            "topic": "Basics",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "2a",
            "topic": "Intermediate Path A",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "intermediate"
        },
        {
            "id": "2b",
            "topic": "Intermediate Path B",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "intermediate"
        },
        {
            "id": "3",
            "topic": "Advanced",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["2a", "2b"],
            "technical_level": "advanced"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert result.is_valid
    assert not result.issues
    assert result.confidence_score == 1.0

def test_excessive_branching(validator):
    """Test detection of excessive branching (too many alternative paths)"""
    nodes = [
        {
            "id": "1",
            "topic": "Root Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        }
    ]
    
    # Add more than max_branching_factor dependent nodes
    for i in range(4):  # Exceeds max_branching_factor of 3
        nodes.append({
            "id": f"child{i+1}",
            "topic": f"Child Topic {i+1}",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "intermediate"
        })
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("too many dependent nodes" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_excessive_prerequisites(validator):
    """Test detection of excessive prerequisites"""
    # Create nodes with more than max_prerequisites_per_node prerequisites
    prereqs = [f"prereq{i+1}" for i in range(5)]  # Exceeds max_prerequisites_per_node of 4
    nodes = [
        {
            "id": "target",
            "topic": "Target Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": prereqs,
            "technical_level": "advanced"
        }
    ]
    
    # Add prerequisite nodes
    for prereq_id in prereqs:
        nodes.append({
            "id": prereq_id,
            "topic": f"Prerequisite {prereq_id}",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "intermediate"
        })
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("too many prerequisites" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_imbalanced_technical_levels(validator):
    """Test detection of imbalanced technical level distribution"""
    nodes = []
    # Add many beginner nodes (more than 50% of total)
    for i in range(6):
        nodes.append({
            "id": f"beginner{i+1}",
            "topic": f"Beginner Topic {i+1}",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        })
    
    # Add a few nodes at other levels
    for level in ["intermediate", "advanced", "expert"]:
        nodes.append({
            "id": level,
            "topic": f"{level.capitalize()} Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": level
        })
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("Imbalanced technical level distribution" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_missing_technical_levels(validator):
    """Test detection of missing technical levels"""
    nodes = [
        {
            "id": "1",
            "topic": "Beginner Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "2",
            "topic": "Expert Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["1"],
            "technical_level": "expert"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("Missing technical levels" in issue for issue in result.issues)
    assert "intermediate" in next(issue for issue in result.issues if "Missing technical levels" in issue)
    assert "advanced" in next(issue for issue in result.issues if "Missing technical levels" in issue)
    assert result.confidence_score < 1.0

def test_multiple_bottlenecks(validator):
    """Test detection of multiple bottleneck nodes"""
    nodes = [
        {
            "id": "start",
            "topic": "Start Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "bottleneck1",
            "topic": "Bottleneck 1",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["start"],
            "technical_level": "intermediate"
        },
        {
            "id": "bottleneck2",
            "topic": "Bottleneck 2",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["bottleneck1"],
            "technical_level": "intermediate"
        },
        {
            "id": "end1",
            "topic": "End Topic 1",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["bottleneck2"],
            "technical_level": "advanced"
        },
        {
            "id": "end2",
            "topic": "End Topic 2",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["bottleneck2"],
            "technical_level": "advanced"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert not result.is_valid
    assert any("Multiple bottleneck nodes detected" in issue for issue in result.issues)
    assert result.confidence_score < 1.0

def test_balanced_structure(validator):
    """Test validation of a well-balanced knowledge map structure"""
    nodes = [
        # Beginner level
        {
            "id": "b1",
            "topic": "Basic Concept 1",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        {
            "id": "b2",
            "topic": "Basic Concept 2",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": [],
            "technical_level": "beginner"
        },
        # Intermediate level with moderate branching
        {
            "id": "i1",
            "topic": "Intermediate Topic 1",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["b1"],
            "technical_level": "intermediate"
        },
        {
            "id": "i2",
            "topic": "Intermediate Topic 2",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["b2"],
            "technical_level": "intermediate"
        },
        # Advanced level with merged paths
        {
            "id": "a1",
            "topic": "Advanced Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["i1", "i2"],
            "technical_level": "advanced"
        },
        # Expert level
        {
            "id": "e1",
            "topic": "Expert Topic",
            "description": "A comprehensive description that meets the minimum length requirement.",
            "required_prerequisites": ["a1"],
            "technical_level": "expert"
        }
    ]
    
    result = validator.validate_map(nodes)
    assert result.is_valid
    assert not result.issues
    assert result.confidence_score == 1.0 