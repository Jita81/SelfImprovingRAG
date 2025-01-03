from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class Document(BaseModel):
    """Base document model for knowledge storage"""
    content: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}
    confidence_score: float = Field(ge=0.0, le=1.0)
    validation_status: str = "unverified"
    prerequisites: List[str] = []  # List of prerequisite document IDs
    dependencies: Dict[str, str] = {}  # Map of document ID to dependency type (e.g. "requires", "references")

class KnowledgePrerequisite(BaseModel):
    """Required knowledge or context"""
    topic: str
    importance: str  # "required" or "recommended"
    description: str
    validation_criteria: List[str]

class OutputRequirement(BaseModel):
    """Specification for required output format/content"""
    format: str
    structure: Dict[str, Any]
    validation_rules: List[str]
    examples: List[Dict[str, str]]

class UseCaseDefinition(BaseModel):
    """Comprehensive use case specification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    domain: str
    technical_level: str  # "beginner", "intermediate", "expert"
    success_criteria: List[str]
    output_requirements: Dict[str, Any]
    knowledge_prerequisites: List[Any] = []
    example_queries: List[Dict[str, str]] = []
