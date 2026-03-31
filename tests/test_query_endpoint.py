"""Tests for POST /queries/ (JSON load + retrieval + mocked LLM)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("sklearn")

from src.api import api as api_module


@pytest.fixture
def client():
    return TestClient(api_module.app)


@patch.object(api_module.llm_service, "answer_query", return_value="mocked answer")
def test_queries_parses_knowledge_map_and_returns_retrieval_metadata(mock_answer, client):
    response = client.post(
        "/queries/",
        json={
            "query": "epic breakdown and features",
            "use_case": "Epic breakdown",
            "domain": "feature_breakdown",
            "top_k": 4,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["answer"] == "mocked answer"
    assert body["retrieval"]["method"] == "tfidf_cosine"
    assert body["retrieval"]["top_k"] == 4
    assert len(body["retrieval"]["retrieved_item_ids"]) <= 4
    mock_answer.assert_called_once()
    call_kw = mock_answer.call_args.kwargs
    assert "retrieved_items" in call_kw
    assert len(call_kw["retrieved_items"]) <= 4


def test_queries_unknown_domain_404(client):
    response = client.post(
        "/queries/",
        json={
            "query": "x",
            "use_case": "y",
            "domain": "nonexistent_domain_xyz",
        },
    )
    assert response.status_code == 404
