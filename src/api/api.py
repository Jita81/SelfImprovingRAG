from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional
import json
import os
from dotenv import load_dotenv

from src.services.llm_service import LLMService
from src.services.knowledge_retrieval import get_knowledge_retrieval_service
from src.services.pattern_recognition import PatternRecognitionService
from src.services.recovery_management import RecoveryManagementService
from src.services.performance_monitoring import PerformanceMonitoringService, MetricType
from src.models.domain import UseCaseDefinition
from src.models.validation_result import ValidationResult
from src.orchestration.rag_orchestrator import RAGOrchestrator

# Load environment variables
load_dotenv()

# Initialize services
llm_service = LLMService()
retrieval_service = get_knowledge_retrieval_service()
orchestrator = RAGOrchestrator()


class _StubEmbeddings:
    """Deterministic pseudo-embeddings for pattern detection without loading a model."""

    def encode(self, texts: List[str]):
        import numpy as np

        out = []
        for t in texts:
            v = np.zeros(16, dtype=np.float64)
            v[abs(hash(t)) % 16] = 1.0
            out.append(v)
        return np.array(out)


pattern_service = PatternRecognitionService(_StubEmbeddings())
recovery_service = RecoveryManagementService(pattern_service)
perf_monitor = PerformanceMonitoringService()

_validation_history: List[ValidationResult] = []

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
    top_k: int = Field(default=8, ge=1, le=50)

class BugReport(BaseModel):
    use_case: str
    domain: str
    description: str
    steps_to_reproduce: List[str]
    expected_behavior: str
    actual_behavior: str


class ValidationResultPayload(BaseModel):
    is_valid: bool
    issues: List[str]
    confidence_score: float
    timestamp: str


class RecoverRequest(BaseModel):
    validation_result: ValidationResultPayload
    knowledge_map: Dict[str, Any]


class ValidateKnowledgeMapBody(BaseModel):
    """Structured body so FastAPI returns 422 when required fields are missing."""

    nodes: Dict[str, Any]
    edges: List[Any] = Field(default_factory=list)


def _parse_ts(iso: str) -> datetime:
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return datetime.now()


def _validate_knowledge_map_struct(body: Dict[str, Any]) -> ValidationResult:
    issues: List[str] = []
    nodes = body.get("nodes")
    edges = body.get("edges") or []
    if not isinstance(nodes, dict):
        issues.append("Invalid or missing nodes collection")
    elif len(nodes) == 0:
        issues.append("Knowledge map has no nodes")
    if isinstance(edges, list):
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                issues.append(f"Invalid edge at index {i}")
                continue
            if "source" not in edge or "target" not in edge:
                issues.append(f"Invalid edge at index {i}")
                continue
            if isinstance(nodes, dict):
                if edge["source"] not in nodes or edge["target"] not in nodes:
                    issues.append(f"Edge references unknown node at index {i}")
    is_valid = len(issues) == 0
    confidence = 1.0 if is_valid else max(0.2, 0.9 - 0.1 * len(issues))
    return ValidationResult(
        is_valid=is_valid,
        issues=issues,
        confidence_score=confidence,
        timestamp=datetime.now(),
    )


def _pattern_to_json(p) -> Dict[str, Any]:
    return {
        "pattern_type": p.pattern_type,
        "description": p.description,
        "significance": p.significance,
        "occurrences": p.occurrences,
        "first_seen": p.first_seen.isoformat(),
        "last_seen": p.last_seen.isoformat(),
        "related_issues": p.related_issues,
        "metadata": p.metadata,
    }


def _recovery_action_records() -> List[Dict[str, Any]]:
    recovery_actions: List[Dict[str, Any]] = []
    for rec in recovery_service.recovery_history:
        if "start_time" not in rec:
            continue
        entry: Dict[str, Any] = {
            "start_time": rec["start_time"],
            "status": rec.get("status", "unknown"),
        }
        if "end_time" in rec:
            entry["end_time"] = rec["end_time"]
        recovery_actions.append(entry)
    return recovery_actions


def _calculate_metric_bundle(window_hours: int):
    window = timedelta(hours=window_hours)
    patterns = pattern_service.analyze_validation_history(
        _validation_history, min_significance=0.0
    )
    return perf_monitor.calculate_metrics(
        _validation_history,
        patterns,
        _recovery_action_records(),
        window_size=window,
    )


def _metrics_dict(window_hours: int) -> Dict[str, Any]:
    calculated = _calculate_metric_bundle(window_hours)
    window = timedelta(hours=window_hours)
    out: Dict[str, Any] = {m.value: 0.0 for m in MetricType}
    for m in calculated.values():
        out[m.metric_type.value] = m.value
    out["window_size"] = int(window.total_seconds())
    out["timestamp"] = datetime.now().isoformat()
    return out


def _alerts_for_window(window_hours: int) -> List[Dict[str, Any]]:
    calculated = _calculate_metric_bundle(window_hours)
    raw_alerts = perf_monitor.check_alerts(calculated)
    alerts = []
    for a in raw_alerts:
        mt = a["metric_type"]
        alerts.append(
            {
                "metric_type": mt.value if isinstance(mt, MetricType) else str(mt),
                "current_value": a["current_value"],
                "threshold": a["threshold"],
                "timestamp": a["timestamp"].isoformat()
                if hasattr(a["timestamp"], "isoformat")
                else a["timestamp"],
                "metadata": a.get("metadata", {}),
            }
        )
    return alerts


# Routes
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/validate")
async def validate_knowledge_map(body: ValidateKnowledgeMapBody):
    vr = _validate_knowledge_map_struct(body.model_dump())
    _validation_history.append(vr)
    return {
        "is_valid": vr.is_valid,
        "issues": vr.issues,
        "confidence_score": vr.confidence_score,
        "timestamp": vr.timestamp.isoformat(),
    }


@app.get("/patterns")
async def get_patterns(min_significance: float = 0.3):
    patterns = pattern_service.analyze_validation_history(
        _validation_history, min_significance=min_significance
    )
    return [_pattern_to_json(p) for p in patterns]


@app.post("/recover")
async def execute_recovery(req: RecoverRequest):
    vr = ValidationResult(
        is_valid=req.validation_result.is_valid,
        issues=list(req.validation_result.issues),
        confidence_score=req.validation_result.confidence_score,
        timestamp=_parse_ts(req.validation_result.timestamp),
    )
    if vr.is_valid:
        raise HTTPException(status_code=400, detail="Cannot recover from valid result")

    action = recovery_service.analyze_failure(vr, list(_validation_history))
    if action is None:
        raise HTTPException(status_code=400, detail="No recovery action available")

    context = {"knowledge_map": req.knowledge_map, "validation_system": {}}
    if action.strategy.value == "revalidation":
        context["validation_system"] = {"stub": True}

    success = recovery_service.execute_recovery(action, context)
    return success


@app.get("/metrics")
async def get_metrics(window_size: int = 24):
    return _metrics_dict(window_size)


@app.get("/alerts")
async def get_alerts():
    return _alerts_for_window(24)


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
            
        with open(knowledge_map_path, "r", encoding="utf-8") as f:
            knowledge_map = json.load(f)

        retrieved, scores = retrieval_service.retrieve(
            domain=query.domain,
            knowledge_map_path=knowledge_map_path,
            query=query.query,
            top_k=query.top_k,
        )

        answer = llm_service.answer_query(
            query=query.query,
            use_case=query.use_case,
            knowledge_map=knowledge_map,
            retrieved_items=retrieved,
            retrieval_scores=scores,
        )

        cited_ids = [
            item.get("id")
            for item in retrieved
            if isinstance(item, dict) and item.get("id") is not None
        ]

        return {
            "status": "success",
            "answer": answer,
            "retrieval": {
                "method": "tfidf_cosine",
                "top_k": query.top_k,
                "retrieved_item_ids": cited_ids,
                "scores": scores,
            },
        }
    except HTTPException:
        raise
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