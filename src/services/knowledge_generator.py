from typing import List, Dict, Any, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from ..models.knowledge_map import KnowledgeMap, KnowledgeNode
from ..models.domain import UseCaseDefinition, Document
from datetime import datetime
import uuid
import asyncio
from enum import Enum

class GenerationStatus(Enum):
    SUCCESS = "success"
    RETRY = "retry"
    FAILED = "failed"

class GeneratedKnowledge:
    def __init__(self, document: Optional[Document], success: bool, issues: List[str] = None, retry_count: int = 0):
        self.document = document
        self.success = success
        self.issues = issues or []
        self.retry_count = retry_count

class KnowledgeGenerator:
    def __init__(self, llm: ChatOpenAI, max_retries: int = 3):
        self.llm = llm
        self.max_retries = max_retries
        self.chain = self._setup_chain()
        self.timeout = 30.0  # Default timeout
        
    def set_timeout(self, timeout: float):
        """Set the timeout for LLM calls"""
        self.timeout = timeout

    def _setup_chain(self):
        prompt = PromptTemplate(
            template="""Generate comprehensive knowledge content for this topic.

Topic Information:
Name: {topic}
Description: {description}
Prerequisites: {prerequisites}
Validation Criteria: {validation_criteria}

Context:
Domain: {domain}
Technical Level: {technical_level}
Attempt: {attempt}  # Added to help adjust generation strategy

Requirements:
1. Content must be comprehensive and accurate
2. Must reference and build upon prerequisite knowledge
3. Must satisfy all validation criteria
4. Must include practical examples
5. Must be appropriate for the technical level

{additional_instructions}  # Added for retry guidance

Return as JSON with format:
{{
    "content": "The detailed knowledge content",
    "references": ["List of prerequisite concepts used"],
    "examples": ["List of practical examples"],
    "validation_points": ["How content meets each validation criterion"]
}}""",
            input_variables=["topic", "description", "prerequisites", "validation_criteria", 
                           "domain", "technical_level", "attempt", "additional_instructions"]
        )
        
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser
        return chain

    def _get_retry_instructions(self, attempt: int, previous_issues: List[str]) -> str:
        if not previous_issues:
            return "Focus on clarity and completeness."
        
        if attempt == 1:
            return f"Previous attempt had issues: {previous_issues}. Try to be more detailed and specific."
        elif attempt == 2:
            return "Break down complex concepts into simpler explanations. Include more examples."
        else:
            return "Focus only on the most essential concepts. Simplify the explanation significantly."

    async def _attempt_generation(self, 
                                node: KnowledgeNode,
                                knowledge_map: KnowledgeMap,
                                use_case: UseCaseDefinition,
                                prereq_contents: List[str],
                                attempt: int,
                                previous_issues: List[str]) -> Tuple[GenerationStatus, Optional[Document], List[str]]:
        """Single attempt at content generation with specific parameters"""
        try:
            # Add timeout to LLM call
            result = await asyncio.wait_for(
                self.chain.ainvoke({
                    "topic": node.topic,
                    "description": node.description,
                    "prerequisites": str(prereq_contents),
                    "validation_criteria": str(node.validation_criteria),
                    "domain": use_case.domain,
                    "technical_level": use_case.technical_level,
                    "attempt": str(attempt),
                    "additional_instructions": self._get_retry_instructions(attempt, previous_issues)
                }),
                timeout=self.timeout  # Use configured timeout
            )
            
            # Validate the generated content
            current_issues = []
            
            # Check content length and quality
            if not result.get("content"):
                return GenerationStatus.RETRY, None, ["No content generated"]
            
            content = result["content"].strip()
            if len(content) < 200:  # Increased minimum length
                current_issues.append("Generated content too short")
            
            # Check for code examples
            examples = result.get("examples", [])
            if not examples:
                current_issues.append("No examples provided")
            
            # Check for specific example requirements
            for criterion in node.validation_criteria:
                if "example" in criterion.lower():
                    if "at least" in criterion.lower():
                        try:
                            required_count = int(''.join(filter(str.isdigit, criterion)))
                            if len(examples) < required_count:
                                current_issues.append(f"Insufficient examples: {len(examples)} provided, need at least {required_count}")
                        except ValueError:
                            current_issues.append(f"Example count requirement not met for: {criterion}")
            
            # Check for validation points
            validation_points = result.get("validation_points", [])
            if len(validation_points) < len(node.validation_criteria):
                current_issues.append(f"Not all validation criteria addressed: {len(validation_points)} of {len(node.validation_criteria)}")
            
            # Check for code snippets in content
            if "code" in " ".join(node.validation_criteria).lower():
                code_lines = [line for line in content.split('\n') 
                            if line.strip().startswith(('def ', 'class ', 'import ', 'from ', 'async ', 'with ', 'try:', 'if ', 'for ', 'while '))]
                if not code_lines:
                    current_issues.append("No code snippets found in content")
            
            # Check for comprehensive coverage
            if any("ALL" in criterion or "comprehensive" in criterion.lower() for criterion in node.validation_criteria):
                # For comprehensive requirements, content should be more substantial
                if len(content) < 500:  # Even longer for comprehensive content
                    current_issues.append("Content not comprehensive enough")
                if len(examples) < 3:
                    current_issues.append("Need more examples for comprehensive coverage")
                
                # Check for missing validation criteria coverage
                covered_criteria = set()
                for point in validation_points:
                    for criterion in node.validation_criteria:
                        if any(keyword in point.lower() for keyword in criterion.lower().split()):
                            covered_criteria.add(criterion)
                
                missing_criteria = set(node.validation_criteria) - covered_criteria
                if missing_criteria:
                    current_issues.append(f"Missing coverage for criteria: {', '.join(missing_criteria)}")
            
            # If this is the last attempt and we still have issues, mark as failed
            if current_issues and attempt >= self.max_retries:
                return GenerationStatus.FAILED, None, current_issues
            
            # If we have issues but can retry, do so
            if current_issues:
                return GenerationStatus.RETRY, None, current_issues
            
            doc = Document(
                content=result["content"],
                source=f"generated_{node.id}_attempt_{attempt}",
                timestamp=datetime.now(),
                metadata={
                    "node_id": node.id,
                    "references": result["references"],
                    "examples": result["examples"],
                    "validation_points": result["validation_points"],
                    "generation_attempt": attempt
                },
                confidence_score=1.0 / attempt,  # Lower confidence for later attempts
                validation_status="generated"
            )
            
            return GenerationStatus.SUCCESS, doc, []
            
        except asyncio.TimeoutError:
            return GenerationStatus.RETRY, None, ["Generation timed out"]
        except Exception as e:
            if attempt >= self.max_retries:
                return GenerationStatus.FAILED, None, [f"Generation error: {str(e)}"]
            return GenerationStatus.RETRY, None, [f"Generation error: {str(e)}"]

    async def generate_content(self, 
                             node: KnowledgeNode, 
                             knowledge_map: KnowledgeMap,
                             use_case: UseCaseDefinition,
                             prerequisite_docs: List[Document] = None) -> GeneratedKnowledge:
        """Generate content for a knowledge node with retry mechanism"""
        prerequisite_docs = prerequisite_docs or []
        
        # Get prerequisite content
        prereq_contents = []
        for prereq_id in node.required_prerequisites:
            matching_docs = [d for d in prerequisite_docs 
                           if d.metadata.get("node_id") == prereq_id]
            if not matching_docs:
                return GeneratedKnowledge(
                    document=None,
                    success=False,
                    issues=[f"Missing prerequisite content for {prereq_id}"]
                )
            prereq_contents.append(matching_docs[0].content)

        all_issues = []
        for attempt in range(1, self.max_retries + 1):
            status, doc, current_issues = await self._attempt_generation(
                node, knowledge_map, use_case, prereq_contents, attempt, all_issues
            )
            
            if status == GenerationStatus.SUCCESS:
                return GeneratedKnowledge(
                    document=doc,
                    success=True,
                    retry_count=attempt - 1
                )
            
            all_issues.extend(current_issues)
            if status == GenerationStatus.FAILED:
                break
            
            # Reduced delay between retries
            if attempt < self.max_retries:
                await asyncio.sleep(0.1)  # 100ms delay
        
        # If we get here, we've failed after all retries
        # Return all unique issues encountered
        unique_issues = list(set(all_issues))  # Remove duplicates
        return GeneratedKnowledge(
            document=None,
            success=False,
            issues=unique_issues,
            retry_count=self.max_retries
        )

    async def generate_all(self, 
                          knowledge_map: KnowledgeMap,
                          use_case: UseCaseDefinition) -> List[GeneratedKnowledge]:
        """Generate content for all nodes in dependency order"""
        results = []
        generated_docs = []
        
        try:
            sequence = knowledge_map.get_generation_sequence()
            
            for node in sequence:
                result = await self.generate_content(
                    node, 
                    knowledge_map,
                    use_case,
                    generated_docs
                )
                results.append(result)
                if result.success:
                    generated_docs.append(result.document)
                else:
                    break
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                # Return what we have so far
                return results
            raise
                    
        return results 