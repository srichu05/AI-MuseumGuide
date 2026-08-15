"""NLP preprocessing utilities."""
from __future__ import annotations

import re

import nltk
import spacy

from config import SPACY_MODEL

_nlp = None


def _ensure_nltk():
    for resource in ("punkt", "punkt_tab", "stopwords", "wordnet"):
        try:
            nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
        except Exception:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass


def get_nlp():
    global _nlp
    if _nlp is None:
        _ensure_nltk()
        try:
            _nlp = spacy.load(SPACY_MODEL)
        except Exception:
            try:
                from spacy.cli import download
                download(SPACY_MODEL)
                _nlp = spacy.load(SPACY_MODEL)
            except Exception:
                _nlp = spacy.blank("en")
    return _nlp


def preprocess_text(text: str) -> dict:
    """Tokenize and normalize user query."""
    nlp = get_nlp()
    doc = nlp(text.strip())
    tokens = [t.text.lower() for t in doc if not t.is_space]
    lemmas = [t.lemma_.lower() for t in doc if not t.is_punct and not t.is_space]
    return {
        "original": text,
        "normalized": " ".join(lemmas),
        "tokens": tokens,
        "lemmas": lemmas,
        "doc": doc,
    }


def simple_tokenize(text: str) -> list[str]:
    text = re.sub(r"[^\w\s'-]", " ", text.lower())
    return [t for t in text.split() if t]
