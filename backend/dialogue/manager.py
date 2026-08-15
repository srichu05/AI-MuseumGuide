"""Local dialogue state manager."""
from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any


class DialogueManager:
    def __init__(self):
        self._sessions: dict[str, dict[str, Any]] = {}

    def create_session(self) -> str:
        sid = str(uuid.uuid4())
        self._sessions[sid] = self._empty_state()
        return sid

    def _empty_state(self) -> dict[str, Any]:
        return {
            "current_artifact": None,
            "current_artist": None,
            "current_period": None,
            "last_intent": None,
            "last_query": None,
            "target": None,
        }

    def get_state(self, session_id: str) -> dict[str, Any]:
        if session_id not in self._sessions:
            self._sessions[session_id] = self._empty_state()
        return deepcopy(self._sessions[session_id])

    def update_state(
        self,
        session_id: str,
        *,
        artifact_id: str | None = None,
        artist_id: str | None = None,
        period_id: str | None = None,
        intent: str | None = None,
        query: str | None = None,
        target: str | None = None,
    ) -> dict[str, Any]:
        if session_id not in self._sessions:
            self._sessions[session_id] = self._empty_state()
        state = self._sessions[session_id]
        if artifact_id is not None:
            state["current_artifact"] = artifact_id
        if artist_id is not None:
            state["current_artist"] = artist_id
        if period_id is not None:
            state["current_period"] = period_id
        if intent is not None:
            state["last_intent"] = intent
        if query is not None:
            state["last_query"] = query
        if target is not None:
            state["target"] = target
        return deepcopy(state)

    def set_artifact_context(self, session_id: str, artifact: dict[str, Any]) -> dict[str, Any]:
        return self.update_state(
            session_id,
            artifact_id=artifact.get("artifact_id"),
            artist_id=artifact.get("artist_id"),
            period_id=artifact.get("period_id"),
        )
