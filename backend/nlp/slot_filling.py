"""Slot filling from entities and dialogue context."""
from __future__ import annotations

from typing import Any


COREF_PATTERNS = {
    "artifact": [
        "this", "it", "that", "this artwork", "this piece", "this sculpture",
        "this painting", "the artwork", "the piece", "the sculpture", "the painting", "which one"
    ],
    "artist": ["he", "she", "the artist", "him", "her", "they", "his", "hers"],
}


def resolve_coreference(text: str, state: dict[str, Any]) -> dict[str, str | None]:
    lower = text.lower()
    resolved = {"artifact": None, "artist": None, "period": None, "gallery": None, "exhibition": None}

    for pron in COREF_PATTERNS["artifact"]:
        if re_match_word(lower, pron):
            resolved["artifact"] = state.get("current_artifact")
            break
    for pron in COREF_PATTERNS["artist"]:
        if re_match_word(lower, pron):
            resolved["artist"] = state.get("current_artist")
            break

    return resolved


def re_match_word(text: str, word: str) -> bool:
    import re
    return bool(re.search(rf"\b{re.escape(word)}\b", text))


def fill_slots(
    text: str,
    intent: str,
    entities: list[dict],
    state: dict[str, Any],
    db_resolver: Any,
) -> dict[str, Any]:
    """Resolve slots for the current turn."""
    slots: dict[str, Any] = {
        "artifact_id": None,
        "artifact_name": None,
        "artist_id": None,
        "artist_name": None,
        "period_id": None,
        "gallery_id": None,
        "exhibition_id": None,
        "compare_artifact_ids": [],
    }

    coref = resolve_coreference(text, state)

    for ent in entities:
        etype, etext = ent["type"], ent["text"]
        if etype == "ARTIFACT":
            rec = db_resolver.get_artifact_by_name(etext)
            if rec:
                slots["artifact_id"] = rec["artifact_id"]
                slots["artifact_name"] = rec["name"]
        elif etype == "ARTIST":
            rec = db_resolver.get_artist_by_name(etext)
            if rec:
                slots["artist_id"] = rec["artist_id"]
                slots["artist_name"] = rec["name"]
        elif etype == "GALLERY":
            for g in db_resolver.list_galleries():
                if g["name"].lower() == etext.lower():
                    slots["gallery_id"] = g["gallery_id"]
        elif etype == "EXHIBITION":
            for e in db_resolver.list_exhibitions():
                if e["name"].lower() == etext.lower():
                    slots["exhibition_id"] = e["exhibition_id"]

    if not slots["artifact_id"] and coref["artifact"]:
        rec = db_resolver.get_artifact_by_id(coref["artifact"]) if coref["artifact"] else None
        if not rec and coref["artifact"]:
            rec = db_resolver.get_artifact_by_name(coref["artifact"])
        if rec:
            slots["artifact_id"] = rec["artifact_id"]
            slots["artifact_name"] = rec["name"]

    if not slots["artist_id"] and coref["artist"]:
        rec = db_resolver.get_artist_by_id(coref["artist"]) if coref["artist"] else None
        if rec:
            slots["artist_id"] = rec["artist_id"]
            slots["artist_name"] = rec["name"]

    # Fallback to dialogue state
    if not slots["artifact_id"] and state.get("current_artifact"):
        rec = db_resolver.get_artifact_by_id(state["current_artifact"])
        if rec:
            slots["artifact_id"] = rec["artifact_id"]
            slots["artifact_name"] = rec["name"]

    if not slots["artist_id"] and state.get("current_artist"):
        rec = db_resolver.get_artist_by_id(state["current_artist"])
        if rec:
            slots["artist_id"] = rec["artist_id"]
            slots["artist_name"] = rec["name"]

    return slots
