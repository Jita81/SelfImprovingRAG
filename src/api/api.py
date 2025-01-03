from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from src.orchestration.rag_orchestrator import RAGOrchestrator
from src.models.domain import UseCaseDefinition
import json
import os

app = FastAPI(title="Self-Improving RAG API")
orchestrator = RAGOrchestrator()

class UseCase(BaseModel):
    name: str
    description: str
    acceptance_criteria: List[str]
    domain: str

class Query(BaseModel):
    use_case: str
    domain: str
    query: str

class Bug(BaseModel):
    use_case: str
    domain: str
    description: str
    steps_to_reproduce: List[str]
    expected_behavior: str
    actual_behavior: str

@app.post("/use-cases/", response_model=Dict)
async def create_use_case(use_case: UseCase):
    """Create a new use case and generate its RAG knowledge base"""
    try:
        # Format use case description with acceptance criteria
        full_description = f"{use_case.description}\n\nAcceptance Criteria:\n"
        for i, criterion in enumerate(use_case.acceptance_criteria, 1):
            full_description += f"{i}. {criterion}\n"

        # Create UseCaseDefinition object
        use_case_def = UseCaseDefinition(
            name=use_case.name,
            description=full_description,
            domain=use_case.domain,
            technical_level="intermediate",  # Default to intermediate
            success_criteria=use_case.acceptance_criteria,
            output_requirements={
                "format": "text",
                "structure": {"type": "explanation"},
                "validation_rules": ["Must include examples"],
                "examples": []
            },
            knowledge_prerequisites=[],
            example_queries=[]
        )

        # Process use case and generate RAG
        results = orchestrator.process_use_case(use_case_def)
        
        return {
            "status": "success",
            "message": f"Use case '{use_case.name}' processed successfully",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/queries/", response_model=Dict)
async def query_rag(query: Query):
    """Query the RAG system for a specific use case"""
    try:
        # Load knowledge base for the domain
        domain_dir = f"data/knowledge_bases/{query.domain}"
        knowledge_map_path = os.path.join(domain_dir, "knowledge_map.json")
        
        if not os.path.exists(knowledge_map_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Knowledge base not found for domain: {query.domain}"
            )
            
        with open(knowledge_map_path, "r") as f:
            knowledge_map = json.load(f)
            
        # Use LLM to answer query using RAG knowledge
        response = orchestrator.llm_service.answer_query(
            query=query.query,
            use_case=query.use_case,
            knowledge_map=knowledge_map
        )
        
        return {
            "status": "success",
            "answer": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bugs/", response_model=Dict)
async def report_bug(bug: Bug):
    """Report a bug to improve the RAG system"""
    try:
        print(f"\nReceived bug report:")
        print(f"Use case: {bug.use_case}")
        print(f"Domain: {bug.domain}")
        print(f"Description: {bug.description}")
        print(f"Steps: {bug.steps_to_reproduce}")
        print(f"Expected: {bug.expected_behavior}")
        print(f"Actual: {bug.actual_behavior}\n")
        
        # Check if knowledge base exists
        domain_dir = f"data/knowledge_bases/{bug.domain}"
        knowledge_map_path = os.path.join(domain_dir, "knowledge_map.json")
        test_cases_path = os.path.join(domain_dir, "test_cases.json")
        
        if not os.path.exists(knowledge_map_path) or not os.path.exists(test_cases_path):
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base not found for domain: {bug.domain}. Please create a use case first."
            )
            
        try:
            with open(knowledge_map_path, "r") as f:
                knowledge_map = json.load(f)
            with open(test_cases_path, "r") as f:
                test_cases = json.load(f)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading knowledge base files: {str(e)}"
            )
        
        # Format bug report
        bug_description = f"""Bug Report:
Description: {bug.description}

Steps to Reproduce:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(bug.steps_to_reproduce))}

Expected Behavior: {bug.expected_behavior}
Actual Behavior: {bug.actual_behavior}
"""
        
        try:
            # Process bug report and improve RAG
            results = orchestrator.process_bug_report(
                bug_description,
                bug.use_case,
                bug.domain
            )
            
            return {
                "status": "success",
                "message": "Bug report processed successfully",
                "improvements": results
            }
        except Exception as e:
            print(f"Error processing bug report: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing bug report: {str(e)}"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error handling bug report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "name": "Self-Improving RAG API",
        "version": "1.0.0",
        "endpoints": [
            "/use-cases/",
            "/queries/",
            "/bugs/"
        ]
    } 