from typing import List, Dict, Any, Set, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from ..models.knowledge_map import KnowledgeMap, KnowledgeNode
from ..models.domain import UseCaseDefinition

class ValidationResult:
    def __init__(self, is_valid: bool, issues: List[str], coverage_score: float):
        self.is_valid = is_valid
        self.issues = issues
        self.coverage_score = coverage_score

class KnowledgeMapValidator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.chain = self._setup_chain()
    
    def _setup_chain(self):
        prompt = PromptTemplate(
            template="""Analyze this knowledge map for completeness and validity.

Use Case:
Name: {name}
Description: {description}
Success Criteria: {success_criteria}

Knowledge Map:
{knowledge_map}

Validate the following aspects and categorize issues:
1. Critical Requirements:
   - All success criteria must be covered by the knowledge topics
   - No circular dependencies
   - Core topics must be present

2. Improvement Suggestions:
   - Optimal ordering of prerequisites
   - Additional validation criteria
   - Enhanced topic coverage

Return as JSON with format:
{{
    "is_valid": true/false,  # Should be true if all critical requirements are met
    "critical_issues": [
        "description of issues that must be fixed"
    ],
    "improvement_suggestions": [
        "suggestions for making the map better"
    ],
    "coverage_score": 0.0-1.0  # Based on critical requirements only
}}""",
            input_variables=["name", "description", "success_criteria", "knowledge_map"]
        )
        
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser
        return chain

    def _check_circular_dependencies(self, nodes: List[KnowledgeNode]) -> List[str]:
        """Check for circular dependencies in the knowledge map"""
        issues = []
        node_map = {node.id: node for node in nodes}
        visited = set()
        path = set()

        def visit(node_id: str) -> bool:
            if node_id in path:
                cycle = list(path)
                start = cycle.index(node_id)
                issues.append(f"Circular dependency found: {' -> '.join(cycle[start:] + [node_id])}")
                return True
            if node_id in visited:
                return False
                
            visited.add(node_id)
            path.add(node_id)
            
            node = node_map[node_id]
            for prereq in node.required_prerequisites:
                if visit(prereq):
                    return True
                    
            path.remove(node_id)
            return False

        for node in nodes:
            visit(node.id)
            
        return issues

    async def validate_map(self, knowledge_map: KnowledgeMap, use_case: UseCaseDefinition) -> ValidationResult:
        """Validate the knowledge map against the use case requirements"""
        # First, check for structural issues (circular dependencies)
        structural_issues = self._check_circular_dependencies(knowledge_map.nodes)
        if structural_issues:
            return ValidationResult(False, structural_issues, 0.0)

        # Then use LLM to check for completeness and semantic validity
        try:
            result = await self.chain.ainvoke({
                "name": use_case.name,
                "description": use_case.description,
                "success_criteria": str(use_case.success_criteria),
                "knowledge_map": str([{
                    "topic": node.topic,
                    "description": node.description,
                    "prerequisites": node.required_prerequisites,
                    "validation_criteria": node.validation_criteria
                } for node in knowledge_map.nodes])
            })
            
            # Combine structural issues with critical issues
            all_issues = structural_issues + result.get("critical_issues", [])
            
            return ValidationResult(
                len(all_issues) == 0,  # Valid only if no critical issues
                all_issues,
                result["coverage_score"]
            )
        except Exception as e:
            return ValidationResult(False, [f"Validation failed: {str(e)}"], 0.0) 