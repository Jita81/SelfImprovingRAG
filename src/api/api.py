from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

from src.services.llm_service import LLMService
from src.models.domain import UseCaseDefinition
from src.orchestration.rag_orchestrator import RAGOrchestrator

# Load environment variables
load_dotenv()

# Initialize services
llm_service = LLMService()
orchestrator = RAGOrchestrator()

# Create FastAPI app
app = FastAPI(
    title="Self-Improving RAG System",
    description="A sophisticated RAG system that continuously improves its knowledge base",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Query(BaseModel):
    query: str
    use_case: str
    domain: str

class BugReport(BaseModel):
    use_case: str
    domain: str
    description: str
    steps_to_reproduce: List[str]
    expected_behavior: str
    actual_behavior: str

# Routes
@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Self-Improving RAG System API is running",
        "version": "1.0.0"
    }

@app.post("/use-cases/")
async def create_use_case(use_case: UseCaseDefinition):
    try:
        results = orchestrator.process_use_case(use_case)
        return {
            "status": "success",
            "message": f"Use case '{use_case.name}' processed successfully",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/queries/")
async def process_query(query: Query):
    try:
        # Load knowledge map
        domain_dir = f"data/knowledge_bases/{query.domain}"
        knowledge_map_path = os.path.join(domain_dir, "knowledge_map.json")
        
        if not os.path.exists(knowledge_map_path):
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge map not found for domain: {query.domain}"
            )
            
        with open(knowledge_map_path, "r") as f:
            knowledge_map = f.read()
            
        # Process query
        response = llm_service.answer_query(
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

@app.post("/bugs/")
async def report_bug(bug: BugReport):
    try:
        results = orchestrator.process_bug_report(
            bug_description=bug.description,
            use_case=bug.use_case,
            domain=bug.domain
        )
        return {
            "status": "success",
            "message": "Bug report processed successfully",
            "improvements": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 