"""Information retrieval: BM25 primary, TF-IDF baseline."""
from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import INDEX_DIR
from nlp.preprocessing import simple_tokenize


@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    score: float
    title: str
    source_type: str
    document_id: str
    metadata: dict[str, Any]


class DocumentIndex:
    def __init__(self):
        self.chunks: list[dict[str, Any]] = []
        self._bm25: BM25Okapi | None = None
        self._tfidf: TfidfVectorizer | None = None
        self._tfidf_matrix = None
        self._tokenized: list[list[str]] = []

    def build(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks = chunks
        self._tokenized = [simple_tokenize(c["text"]) for c in chunks]
        self._bm25 = BM25Okapi(self._tokenized)
        self._tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=50000)
        texts = [c["text"] for c in chunks]
        self._tfidf_matrix = self._tfidf.fit_transform(texts)
        self._save()

    def _save(self) -> None:
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        with open(INDEX_DIR / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
        with open(INDEX_DIR / "bm25.pkl", "wb") as f:
            pickle.dump({"tokenized": self._tokenized}, f)
        with open(INDEX_DIR / "tfidf.pkl", "wb") as f:
            pickle.dump({"vectorizer": self._tfidf, "matrix": self._tfidf_matrix}, f)

    def load(self) -> bool:
        chunk_path = INDEX_DIR / "chunks.pkl"
        if not chunk_path.exists():
            return False
        with open(chunk_path, "rb") as f:
            self.chunks = pickle.load(f)
        with open(INDEX_DIR / "bm25.pkl", "rb") as f:
            data = pickle.load(f)
            self._tokenized = data["tokenized"]
            self._bm25 = BM25Okapi(self._tokenized)
        with open(INDEX_DIR / "tfidf.pkl", "rb") as f:
            data = pickle.load(f)
            self._tfidf = data["vectorizer"]
            self._tfidf_matrix = data["matrix"]
        return True

    def _to_result(self, idx: int, score: float) -> RetrievalResult:
        c = self.chunks[idx]
        meta = json.loads(c.get("metadata_json") or "{}")
        return RetrievalResult(
            chunk_id=c["chunk_id"],
            text=c["text"],
            score=float(score),
            title=c.get("title", "Unknown"),
            source_type=c.get("source_type", "document"),
            document_id=c.get("document_id", ""),
            metadata=meta,
        )

    def search_bm25(self, query: str, top_k: int = 5, artifact_id: str | None = None) -> list[RetrievalResult]:
        if not self._bm25 or not self.chunks:
            return []
        tokens = simple_tokenize(query)
        scores = self._bm25.get_scores(tokens)
        ranked = np.argsort(scores)[::-1]
        results = []
        for idx in ranked:
            if scores[idx] <= 0:
                continue
            if artifact_id and self.chunks[idx].get("artifact_id") and self.chunks[idx]["artifact_id"] != artifact_id:
                continue
            results.append(self._to_result(int(idx), scores[idx]))
            if len(results) >= top_k:
                break
        return results

    def search_tfidf(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        if self._tfidf is None or self._tfidf_matrix is None:
            return []
        q_vec = self._tfidf.transform([query])
        sims = cosine_similarity(q_vec, self._tfidf_matrix).flatten()
        ranked = np.argsort(sims)[::-1]
        return [self._to_result(int(i), sims[i]) for i in ranked[:top_k] if sims[i] > 0]
