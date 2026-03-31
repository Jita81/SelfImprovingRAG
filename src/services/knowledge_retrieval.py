"""Lightweight retrieval over knowledge map items (TF-IDF, no extra services)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _item_to_text(item: Dict[str, Any]) -> str:
    parts = [
        str(item.get("type", "")),
        str(item.get("content", "")),
        " ".join(str(x) for x in item.get("validation_criteria", []) or []),
        " ".join(str(x) for x in item.get("relationships", []) or []),
        str(item.get("id", "")),
    ]
    return " ".join(p for p in parts if p).strip()


class KnowledgeRetrievalService:
    """Per-domain TF-IDF index over knowledge_items, invalidated when the file mtime changes."""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}

    def invalidate(self, domain: str) -> None:
        self._cache.pop(domain, None)

    def _load_map(self, knowledge_map_path: str) -> Dict[str, Any]:
        with open(knowledge_map_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _ensure_index(self, domain: str, knowledge_map_path: str) -> None:
        if not os.path.isfile(knowledge_map_path):
            return
        mtime = os.path.getmtime(knowledge_map_path)
        cached = self._cache.get(domain)
        if cached and cached.get("mtime") == mtime:
            return

        data = self._load_map(knowledge_map_path)
        items: List[Dict[str, Any]] = list(data.get("knowledge_items") or [])
        texts = [_item_to_text(i) for i in items]
        if not texts or not any(texts):
            self._cache[domain] = {
                "mtime": mtime,
                "vectorizer": None,
                "matrix": None,
                "items": items,
            }
            return

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            max_features=8192,
            ngram_range=(1, 2),
            min_df=1,
        )
        matrix = vectorizer.fit_transform(texts)
        self._cache[domain] = {
            "mtime": mtime,
            "vectorizer": vectorizer,
            "matrix": matrix,
            "items": items,
        }

    def retrieve(
        self,
        domain: str,
        knowledge_map_path: str,
        query: str,
        top_k: int = 8,
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        Return top_k knowledge_items by cosine similarity to the query.
        If the index is empty or query is blank, returns all items with score 0.0.
        """
        self._ensure_index(domain, knowledge_map_path)
        cached = self._cache.get(domain)
        if not cached:
            return [], []

        items: List[Dict[str, Any]] = cached["items"]
        if not items:
            return [], []

        vectorizer = cached["vectorizer"]
        matrix = cached["matrix"]
        if vectorizer is None or matrix is None:
            return list(items), [0.0] * len(items)

        q = (query or "").strip()
        if not q:
            return list(items), [0.0] * len(items)

        q_vec = vectorizer.transform([q])
        sims = cosine_similarity(matrix, q_vec).ravel()
        order = sims.argsort()[::-1]
        k = max(1, min(top_k, len(order)))
        top_idx = order[:k]
        retrieved = [items[int(i)] for i in top_idx]
        scores = [float(sims[int(i)]) for i in top_idx]
        return retrieved, scores


_retrieval_singleton: Optional[KnowledgeRetrievalService] = None


def get_knowledge_retrieval_service() -> KnowledgeRetrievalService:
    global _retrieval_singleton
    if _retrieval_singleton is None:
        _retrieval_singleton = KnowledgeRetrievalService()
    return _retrieval_singleton
