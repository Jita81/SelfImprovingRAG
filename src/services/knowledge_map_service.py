import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from ..models.knowledge_map import KnowledgeMap, KnowledgeNode
from ..models.domain import UseCaseDefinition
import uuid

class KnowledgeMapService:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.chain = self._setup_chain()
    
    def _setup_chain(self):
        prompt = PromptTemplate(
            template="""Analyze this use case and create a knowledge map.
            
            Use Case:
            Name: {name}
            Description: {description}
            Domain: {domain}
            Technical Level: {technical_level}
            
            Required Output:
            - List of essential knowledge topics
            - Dependencies between topics
            - Validation criteria for each topic
            
            Return as JSON with format:
            {{
                "nodes": [
                    {{
                        "id": "unique_id",
                        "topic": "topic name",
                        "description": "what needs to be known",
                        "required_prerequisites": ["id1", "id2"],
                        "validation_criteria": ["criterion1", "criterion2"]
                    }}
                ]
            }}
            
            Ensure the JSON is valid and each node has a unique ID.""",
            input_variables=["name", "description", "domain", "technical_level"]
        )
        
        parser = JsonOutputParser()
        
        chain = (
            prompt 
            | self.llm 
            | parser
        )
        
        return chain
    
    async def generate_map(self, use_case: UseCaseDefinition) -> KnowledgeMap:
        """Generate a knowledge map for the given use case"""
        try:
            map_data = await self.chain.ainvoke({
                "name": use_case.name,
                "description": use_case.description,
                "domain": use_case.domain,
                "technical_level": use_case.technical_level
            })
            
            return KnowledgeMap(
                id=str(uuid.uuid4()),
                use_case_id=use_case.id,
                nodes=[KnowledgeNode(**node) for node in map_data["nodes"]]
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON") from e
        except KeyError as e:
            raise ValueError(f"Missing required field in LLM response: {e}") from e 