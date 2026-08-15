"""Entity extraction using spaCy NER + museum entity matching."""
from __future__ import annotations

import re
from typing import Any

from nlp.preprocessing import get_nlp


ENTITY_TYPES = ["ARTIFACT", "ARTIST", "HISTORICAL_PERIOD", "GALLERY", "EXHIBITION", "LOCATION"]


def _match_from_list(text: str, names: list[str], entity_type: str) -> list[dict[str, Any]]:
    found = []
    lower = text.lower()
    for name in sorted(names, key=len, reverse=True):
        pattern = re.escape(name.lower())
        if re.search(rf"\b{pattern}\b", lower):
            found.append({"text": name, "type": entity_type, "start": lower.find(name.lower()), "method": "gazetteer"})
    return found


def extract_entities(text: str, gazetteer: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    nlp = get_nlp()
    doc = nlp(text)
    entities: list[dict[str, Any]] = []

    for ent in doc.ents:
        mapped = None
        if ent.label_ in ("PERSON", "ORG"):
            mapped = "ARTIST"
        elif ent.label_ in ("GPE", "LOC", "FAC"):
            mapped = "LOCATION"
        elif ent.label_ == "DATE":
            mapped = "HISTORICAL_PERIOD"
        if mapped:
            entities.append({
                "text": ent.text,
                "type": mapped,
                "start": ent.start_char,
                "end": ent.end_char,
                "method": "spacy",
            })

    if gazetteer:
        for etype, names in gazetteer.items():
            entities.extend(_match_from_list(text, names, etype))

    # Deduplicate by text+type keeping longest match
    seen = set()
    unique = []
    for e in sorted(entities, key=lambda x: (-len(x["text"]), x["start"])):
        key = (e["text"].lower(), e["type"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return sorted(unique, key=lambda x: x.get("start", 0))
