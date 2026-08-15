"""Extractive factoid QA from retrieved passages."""
from __future__ import annotations

from typing import Any

_qa_pipeline = None


def get_qa_pipeline():
    global _qa_pipeline
    if _qa_pipeline is None:
        try:
            from transformers import pipeline
            from config import QA_MODEL_NAME
            _qa_pipeline = pipeline("question-answering", model=QA_MODEL_NAME, tokenizer=QA_MODEL_NAME)
        except Exception:
            _qa_pipeline = False
    return _qa_pipeline if _qa_pipeline is not False else None


def extract_factoid(question: str, passages: list[str], max_answer_len: int = 128) -> dict[str, Any]:
    qa = get_qa_pipeline()
    if not passages:
        return {"answer": "", "score": 0.0, "passage_index": -1, "method": "none"}

    if qa:
        best = {"answer": "", "score": 0.0, "passage_index": -1, "method": "transformers"}
        for i, passage in enumerate(passages):
            if len(passage.strip()) < 20:
                continue
            try:
                result = qa(question=question, context=passage[:1500], max_answer_len=max_answer_len)
                if result["score"] > best["score"]:
                    best = {
                        "answer": result["answer"],
                        "score": float(result["score"]),
                        "passage_index": i,
                        "method": "transformers",
                    }
            except Exception:
                continue
        if best["score"] > 0.01:
            return best

    keywords = [w for w in question.lower().split() if len(w) > 3]
    for i, passage in enumerate(passages):
        for sent in passage.split("."):
            sent = sent.strip()
            if len(sent) > 30 and any(k in sent.lower() for k in keywords):
                return {"answer": sent, "score": 0.3, "passage_index": i, "method": "keyword"}
    return {"answer": passages[0][:200] if passages else "", "score": 0.1, "passage_index": 0, "method": "fallback"}
