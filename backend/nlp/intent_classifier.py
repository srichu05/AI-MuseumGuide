"""Intent classification using TF-IDF + Logistic Regression with rule fallback."""
from __future__ import annotations

import re
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from config import INTENT_MODEL_PATH

INTENTS = [
    "GREETING",
    "GET_ARTIFACT_INFO",
    "GET_CREATOR",
    "GET_LOCATION",
    "GET_PERIOD",
    "GET_YEAR",
    "GET_HISTORY",
    "GET_DESCRIPTION",
    "GET_OTHER_WORKS",
    "GET_EXHIBITION",
    "GET_GALLERY",
    "COMPARE_ARTIFACTS",
    "HELP",
    "UNKNOWN",
]

TRAINING_DATA = [
    # GREETING
    ("hello", "GREETING"), ("hi there", "GREETING"), ("good morning", "GREETING"),
    ("good afternoon", "GREETING"), ("hey museum guide", "GREETING"), ("greetings", "GREETING"),
    ("hello docent", "GREETING"), ("hi guide", "GREETING"), ("good evening", "GREETING"),
    ("hey there AI", "GREETING"), ("hello computer", "GREETING"), ("welcome", "GREETING"),

    # GET_ARTIFACT_INFO
    ("tell me about this artwork", "GET_ARTIFACT_INFO"), ("what is this piece", "GET_ARTIFACT_INFO"),
    ("info about the thinker", "GET_ARTIFACT_INFO"), ("describe this artifact", "GET_ARTIFACT_INFO"),
    ("give me information about mona lisa", "GET_ARTIFACT_INFO"), ("details on starry night", "GET_ARTIFACT_INFO"),
    ("tell me about the bust of nefertiti", "GET_ARTIFACT_INFO"), ("what can you tell me about this masterpiece", "GET_ARTIFACT_INFO"),
    ("can you explain this painting", "GET_ARTIFACT_INFO"), ("overview of this sculpture", "GET_ARTIFACT_INFO"),
    ("tell me about guernica", "GET_ARTIFACT_INFO"), ("what is the birth of venus", "GET_ARTIFACT_INFO"),

    # GET_CREATOR
    ("who created this", "GET_CREATOR"), ("who made it", "GET_CREATOR"), ("who is the artist", "GET_CREATOR"),
    ("who painted this", "GET_CREATOR"), ("who sculpted this", "GET_CREATOR"), ("who designed this work", "GET_CREATOR"),
    ("who was the sculptor", "GET_CREATOR"), ("who was the painter", "GET_CREATOR"), ("who crafted it", "GET_CREATOR"),
    ("whose work is this", "GET_CREATOR"), ("who painted the starry night", "GET_CREATOR"),
    ("who sculpted the thinker", "GET_CREATOR"), ("who carved this statue", "GET_CREATOR"),

    # GET_LOCATION
    ("where is it located", "GET_LOCATION"), ("where can i find this", "GET_LOCATION"),
    ("which gallery is it in", "GET_LOCATION"), ("what floor", "GET_LOCATION"),
    ("where is the mona lisa displayed", "GET_LOCATION"), ("which room is it in", "GET_LOCATION"),
    ("where in the museum is this piece", "GET_LOCATION"), ("what gallery contains this artwork", "GET_LOCATION"),
    ("how do i find gallery 4", "GET_LOCATION"), ("location of the david sculpture", "GET_LOCATION"),

    # GET_PERIOD
    ("what period is this from", "GET_PERIOD"), ("historical period", "GET_PERIOD"),
    ("what era", "GET_PERIOD"), ("which movement produced this", "GET_PERIOD"),
    ("is this renaissance art", "GET_PERIOD"), ("is it baroque or impressionist", "GET_PERIOD"),
    ("what art movement does this belong to", "GET_PERIOD"), ("cultural period of nefertiti", "GET_PERIOD"),
    ("historical era of this painting", "GET_PERIOD"), ("which artistic period", "GET_PERIOD"),

    # GET_YEAR
    ("when was this made", "GET_YEAR"), ("what year", "GET_YEAR"), ("creation date", "GET_YEAR"),
    ("when was it created", "GET_YEAR"), ("what century", "GET_YEAR"), ("date of creation", "GET_YEAR"),
    ("when did rodin complete this", "GET_YEAR"), ("how old is this artwork", "GET_YEAR"),
    ("when was starry night painted", "GET_YEAR"), ("year of completion", "GET_YEAR"),

    # GET_HISTORY
    ("tell me about its history", "GET_HISTORY"), ("historical significance", "GET_HISTORY"),
    ("what is the historical context", "GET_HISTORY"), ("background story of this piece", "GET_HISTORY"),
    ("why is this artwork famous", "GET_HISTORY"), ("what is the story behind this painting", "GET_HISTORY"),
    ("historical importance of the rosetta stone", "GET_HISTORY"), ("tell me the origin of this work", "GET_HISTORY"),
    ("provenance and history", "GET_HISTORY"), ("why was it created", "GET_HISTORY"),

    # GET_DESCRIPTION
    ("describe this work", "GET_DESCRIPTION"), ("what does it depict", "GET_DESCRIPTION"),
    ("what is shown in this picture", "GET_DESCRIPTION"), ("explain the visual elements", "GET_DESCRIPTION"),
    ("what am i looking at", "GET_DESCRIPTION"), ("describe the scene in this painting", "GET_DESCRIPTION"),
    ("what subject is portrayed", "GET_DESCRIPTION"), ("composition analysis of mona lisa", "GET_DESCRIPTION"),

    # GET_OTHER_WORKS
    ("what other works did he create", "GET_OTHER_WORKS"), ("other paintings by the artist", "GET_OTHER_WORKS"),
    ("more works by this artist", "GET_OTHER_WORKS"), ("what else did van gogh paint", "GET_OTHER_WORKS"),
    ("did rodin make other sculptures", "GET_OTHER_WORKS"), ("show other pieces by michelangelo", "GET_OTHER_WORKS"),
    ("other masterpieces by leonardo", "GET_OTHER_WORKS"), ("which one is the oldest", "GET_OTHER_WORKS"),

    # GET_EXHIBITION
    ("what exhibition is it in", "GET_EXHIBITION"), ("current exhibitions", "GET_EXHIBITION"),
    ("show exhibitions", "GET_EXHIBITION"), ("is this part of a temporary exhibit", "GET_EXHIBITION"),
    ("which exhibit features masters of bronze", "GET_EXHIBITION"), ("exhibitions currently on display", "GET_EXHIBITION"),

    # GET_GALLERY
    ("tell me about the gallery", "GET_GALLERY"), ("which gallery", "GET_GALLERY"),
    ("grand atrium overview", "GET_GALLERY"), ("tell me about impressionist salon", "GET_GALLERY"),
    ("what works are in gallery 3", "GET_GALLERY"), ("gallery description", "GET_GALLERY"),

    # COMPARE_ARTIFACTS
    ("compare these two artworks", "COMPARE_ARTIFACTS"), ("how do they differ", "COMPARE_ARTIFACTS"),
    ("compare mona lisa and girl with a pearl earring", "COMPARE_ARTIFACTS"), ("difference between rodin and bernini", "COMPARE_ARTIFACTS"),
    ("compare starry night with water lilies", "COMPARE_ARTIFACTS"), ("contrast these two sculptures", "COMPARE_ARTIFACTS"),

    # HELP
    ("help", "HELP"), ("what can you do", "HELP"), ("how does this work", "HELP"),
    ("instructions for museum guide", "HELP"), ("what questions can i ask", "HELP"), ("guide capabilities", "HELP"),

    # UNKNOWN
    ("what is the weather today", "UNKNOWN"), ("who won the football match", "UNKNOWN"),
    ("recipe for chocolate cake", "UNKNOWN"), ("stock market prices", "UNKNOWN"),
    ("how to repair a car", "UNKNOWN"), ("quantum computing physics", "UNKNOWN"),
]

RULE_PATTERNS = [
    (r"\b(hello|hi|hey|greetings|good (morning|afternoon|evening))\b", "GREETING"),
    (r"\bwho (created|made|painted|sculpted|designed|crafted|is the artist|was the artist)\b", "GET_CREATOR"),
    (r"\b(where|location|gallery|floor|find it|which room|located in)\b", "GET_LOCATION"),
    (r"\b(period|era|movement|style|century)\b", "GET_PERIOD"),
    (r"\b(when|year|date|created in|completion|how old)\b", "GET_YEAR"),
    (r"\b(histor(y|ical)|significance|context|origin|provenance|story behind|why is it famous)\b", "GET_HISTORY"),
    (r"\b(describe|depict|look like|portray|composition|am i looking at)\b", "GET_DESCRIPTION"),
    (r"\b(tell me about|info about|information about|details on|overview of|explain this)\b", "GET_ARTIFACT_INFO"),
    (r"\b(other works|more (works|paintings|sculptures|pieces)|what else|oldest|newest)\b", "GET_OTHER_WORKS"),
    (r"\bexhibition\b", "GET_EXHIBITION"),
    (r"\bgallery\b", "GET_GALLERY"),
    (r"\bcompare|contrast|difference between\b", "COMPARE_ARTIFACTS"),
    (r"\bhelp|instructions|what can you do\b", "HELP"),
]

_classifier: Pipeline | None = None


def train_classifier() -> Pipeline:
    texts, labels = zip(*TRAINING_DATA)
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("lr", LogisticRegression(max_iter=1000)),
    ])
    clf.fit(list(texts), list(labels))
    INTENT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, INTENT_MODEL_PATH)
    return clf


def load_classifier() -> Pipeline:
    global _classifier
    if _classifier is not None:
        return _classifier
    if INTENT_MODEL_PATH.exists():
        _classifier = joblib.load(INTENT_MODEL_PATH)
    else:
        _classifier = train_classifier()
    return _classifier


def rule_based_intent(text: str) -> str | None:
    lower = text.lower()
    for pattern, intent in RULE_PATTERNS:
        if re.search(pattern, lower):
            return intent
    return None


def classify_intent(text: str) -> dict:
    rule = rule_based_intent(text)
    if rule:
        return {"intent": rule, "confidence": 0.95, "method": "rules"}
    clf = load_classifier()
    intent = clf.predict([text.lower()])[0]
    proba = max(clf.predict_proba([text.lower()])[0])
    if proba < 0.35:
        return {"intent": "UNKNOWN", "confidence": float(proba), "method": "ml"}
    return {"intent": intent, "confidence": float(proba), "method": "ml"}
