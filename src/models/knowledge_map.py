from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class KnowledgeNode(BaseModel):
    """Represents a single node in the knowledge map"""
    id: str
    topic: str
    description: str
    required_prerequisites: List[str] = []
    validation_criteria: List[str] = []
    status: str = "pending"  # pending, in_progress, completed, validated
    metadata: Dict[str, Any] = {}

class KnowledgeMap(BaseModel):
    """Represents the complete knowledge map for a use case"""
    id: str
    use_case_id: str
    nodes: List[KnowledgeNode]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def get_generation_sequence(self) -> List[KnowledgeNode]:
        """Returns nodes in dependency order"""
        # Simple topological sort
        visited = set()
        sequence = []
        
        def visit(node_id: str):
            if node_id in visited:
                return
            node = next(n for n in self.nodes if n.id == node_id)
            for prereq in node.required_prerequisites:
                visit(prereq)
            visited.add(node_id)
            sequence.append(node)
            
        for node in self.nodes:
            visit(node.id)
            
        return sequence 