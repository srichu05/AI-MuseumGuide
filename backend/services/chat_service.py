"""End-to-end chat orchestration — local NLP/IR then GroqCloud generation."""
from __future__ import annotations

import time
from typing import Any

from config import BM25_TOP_K
from database.queries import MuseumQueries
from dialogue.manager import DialogueManager
from ir.retriever import DocumentIndex
from llm.groq_client import GroqClient
from nlp.entity_extractor import extract_entities
from nlp.intent_classifier import classify_intent
from nlp.preprocessing import preprocess_text
from nlp.slot_filling import fill_slots
from qa.factoid import extract_factoid

STRUCTURED_INTENTS = {
    "GET_CREATOR", "GET_LOCATION", "GET_PERIOD", "GET_YEAR",
    "GET_ARTIFACT_INFO", "GET_DESCRIPTION", "GET_OTHER_WORKS",
    "GET_EXHIBITION", "GET_GALLERY", "COMPARE_ARTIFACTS",
}
IR_INTENTS = {"GET_HISTORY", "GET_DESCRIPTION", "GET_ARTIFACT_INFO"}


class ChatService:
    def __init__(
        self,
        queries: MuseumQueries,
        index: DocumentIndex,
        dialogue: DialogueManager,
        groq: GroqClient,
    ):
        self.queries = queries
        self.index = index
        self.dialogue = dialogue
        self.groq = groq

    def _gazetteer(self) -> dict[str, list[str]]:
        return {
            "ARTIFACT": self.queries.get_all_artifact_names(),
            "ARTIST": self.queries.get_all_artist_names(),
            "HISTORICAL_PERIOD": self.queries.get_all_period_names(),
            "GALLERY": self.queries.get_all_gallery_names(),
            "EXHIBITION": self.queries.get_all_exhibition_names(),
        }

    def process(self, session_id: str, query: str) -> dict[str, Any]:
        start = time.time()
        state = self.dialogue.get_state(session_id)
        preprocessed = preprocess_text(query)
        intent_result = classify_intent(query)
        intent = intent_result["intent"]
        entities = extract_entities(query, self._gazetteer())
        slots = fill_slots(query, intent, entities, state, self.queries)

        sqlite_facts: dict[str, Any] = {}
        ir_facts: list[str] = []
        sources: list[dict[str, Any]] = []
        artifact_name = slots.get("artifact_name")

        if intent == "GREETING":
            answer = {
                "answer": "Welcome to the Digital Museum! Upload an artifact image or ask me about any work in our collection.",
                "generated_by": "template",
            }
            self.dialogue.update_state(session_id, intent=intent, query=query)
            return self._build_response(session_id, query, intent, intent_result, entities, slots, answer, sources, start)

        if intent == "HELP":
            answer = {
                "answer": "I can help you learn about artifacts in our collection. Upload an image to identify a work, then ask about its creator, location, history, or related exhibitions. All answers are grounded in our museum database and documents.",
                "generated_by": "template",
            }
            self.dialogue.update_state(session_id, intent=intent, query=query)
            return self._build_response(session_id, query, intent, intent_result, entities, slots, answer, sources, start)

        artifact_id = slots.get("artifact_id")

        if intent in STRUCTURED_INTENTS and artifact_id:
            artifact = self.queries.get_artifact_by_id(artifact_id)
            if artifact:
                artifact_name = artifact["name"]
                self.dialogue.set_artifact_context(session_id, artifact)
                sqlite_facts = self._query_structured(intent, artifact, slots)

        elif intent in IR_INTENTS or intent == "GET_HISTORY":
            retrieval_query = query
            if artifact_name:
                retrieval_query = f"{artifact_name} {query}"
            results = self.index.search_bm25(retrieval_query, top_k=BM25_TOP_K, artifact_id=artifact_id)
            passages = [r.text for r in results]
            for r in results:
                sources.append({
                    "title": r.title,
                    "source_type": r.source_type,
                    "document_id": r.document_id,
                    "chunk_id": r.chunk_id,
                    "score": r.score,
                })
            if passages:
                factoid = extract_factoid(query, passages)
                if factoid["answer"]:
                    ir_facts.append(factoid["answer"])
            if artifact_id and not sqlite_facts:
                artifact = self.queries.get_artifact_by_id(artifact_id)
                if artifact:
                    sqlite_facts = {"name": artifact["name"], "description": artifact.get("description")}

        elif intent == "UNKNOWN":
            answer = {
                "answer": "I'm not sure how to answer that. Try asking about an artifact's creator, location, history, or upload an image first.",
                "generated_by": "template",
            }
            return self._build_response(session_id, query, intent, intent_result, entities, slots, answer, sources, start)

        if not sqlite_facts and not ir_facts and not artifact_name:
            answer = {
                "answer": "Please upload or specify an artifact first so I can answer your question using our museum collection.",
                "generated_by": "template",
            }
            return self._build_response(session_id, query, intent, intent_result, entities, slots, answer, sources, start)

        if sqlite_facts and not sources:
            sources.append({"title": "Museum Artifact Database", "source_type": "sqlite", "document_id": artifact_id or ""})

        answer = self.groq.generate_response(query, artifact_name, sqlite_facts, ir_facts, sources)
        self.dialogue.update_state(
            session_id,
            intent=intent,
            query=query,
            artifact_id=slots.get("artifact_id"),
            artist_id=slots.get("artist_id"),
        )
        return self._build_response(session_id, query, intent, intent_result, entities, slots, answer, sources, start)

    def _query_structured(self, intent: str, artifact: dict, slots: dict) -> dict[str, Any]:
        facts = {"name": artifact["name"]}
        if intent == "GET_CREATOR":
            facts["artist"] = artifact.get("artist_name")
            facts["year"] = artifact.get("year")
        elif intent == "GET_LOCATION":
            facts["gallery"] = artifact.get("gallery_name")
            facts["floor"] = artifact.get("floor")
            facts["location"] = artifact.get("gallery_location")
        elif intent == "GET_PERIOD":
            facts["period"] = artifact.get("period_name")
        elif intent == "GET_YEAR":
            facts["year"] = artifact.get("year")
        elif intent in ("GET_DESCRIPTION", "GET_ARTIFACT_INFO"):
            facts["description"] = artifact.get("description")
            facts["type"] = artifact.get("type")
            facts["artist"] = artifact.get("artist_name")
            facts["year"] = artifact.get("year")
        elif intent == "GET_OTHER_WORKS":
            artist_id = artifact.get("artist_id") or slots.get("artist_id")
            if artist_id:
                works = self.queries.get_other_works_by_artist(artist_id, artifact.get("artifact_id"))
                facts["artist"] = artifact.get("artist_name") or slots.get("artist_name")
                facts["other_works"] = [f"{w['name']} ({w['year']})" for w in works[:10]]
                if works:
                    oldest = min(works, key=lambda x: x["year"])
                    facts["oldest_work"] = f"{oldest['name']} ({oldest['year']})"
        elif intent == "GET_EXHIBITION":
            exhs = self.queries.get_exhibitions_for_artifact(artifact["artifact_id"])
            facts["exhibitions"] = [e["name"] for e in exhs]
        elif intent == "GET_GALLERY":
            facts["gallery"] = artifact.get("gallery_name")
            facts["floor"] = artifact.get("floor")
        return facts

    def _build_response(
        self, session_id, query, intent, intent_result, entities, slots, answer, sources, start
    ) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "query": query,
            "answer": answer.get("answer", ""),
            "intent": intent,
            "intent_confidence": intent_result.get("confidence"),
            "entities": entities,
            "slots": slots,
            "sources": sources,
            "generated_by": answer.get("generated_by", "unknown"),
            "dialogue_state": self.dialogue.get_state(session_id),
            "latency_ms": round((time.time() - start) * 1000, 1),
        }
