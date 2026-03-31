import json
import os
import tempfile

import pytest

from src.services.knowledge_retrieval import KnowledgeRetrievalService
from src.services.llm_service import parse_llm_json


def test_parse_llm_json_object_and_fences():
    assert parse_llm_json('{"a": 1}') == {"a": 1}
    assert parse_llm_json("```json\n{\"b\": 2}\n```") == {"b": 2}
    assert parse_llm_json("Here is data:\n```\n[1,2]\n```") == [1, 2]


def test_retrieval_ranks_relevant_item_first():
    km = {
        "knowledge_items": [
            {
                "id": "KI-A",
                "type": "concept",
                "content": "How to configure Redis caching for sessions.",
                "relationships": [],
                "validation_criteria": [],
            },
            {
                "id": "KI-B",
                "type": "rule",
                "content": "PostgreSQL connection pooling and transaction isolation levels.",
                "relationships": [],
                "validation_criteria": ["VR-1"],
            },
        ]
    }
    svc = KnowledgeRetrievalService()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "knowledge_map.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(km, f)
        items, scores = svc.retrieve("testdom", path, "PostgreSQL transaction isolation", top_k=2)
        assert len(items) == 2
        assert items[0]["id"] == "KI-B"
        assert scores[0] >= scores[1]


def test_retrieval_cache_invalidates_on_mtime_change():
    km1 = {
        "knowledge_items": [
            {
                "id": "KI-1",
                "type": "concept",
                "content": "only alpha keywords here",
                "relationships": [],
                "validation_criteria": [],
            }
        ]
    }
    km2 = {
        "knowledge_items": [
            {
                "id": "KI-2",
                "type": "concept",
                "content": "beta gamma completely different vocabulary",
                "relationships": [],
                "validation_criteria": [],
            }
        ]
    }
    svc = KnowledgeRetrievalService()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "knowledge_map.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(km1, f)
        a, _ = svc.retrieve("d", path, "alpha keywords", top_k=1)
        assert a[0]["id"] == "KI-1"

        import time

        time.sleep(0.05)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(km2, f)
        b, _ = svc.retrieve("d", path, "beta gamma vocabulary", top_k=1)
        assert b[0]["id"] == "KI-2"
