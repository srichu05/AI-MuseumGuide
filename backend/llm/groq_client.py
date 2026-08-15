"""GroqCloud client — vision identification and response generation only."""
from __future__ import annotations

import base64
import json
import re
from typing import Any

from config import GROQ_API_KEY, GROQ_TEXT_MODEL, GROQ_VISION_MODEL


class GroqClient:
    def __init__(self):
        self._client = None
        if GROQ_API_KEY:
            from groq import Groq
            self._client = Groq(api_key=GROQ_API_KEY)

    @property
    def available(self) -> bool:
        return self._client is not None

    def identify_artifact(self, image_bytes: bytes, mime_type: str, artifact_names: list[str]) -> dict[str, Any]:
        if not self.available:
            return {"artifact_name": "UNKNOWN", "confidence": 0.0, "error": "GroqCloud not configured"}

        b64 = base64.b64encode(image_bytes).decode("utf-8")
        names_list = ", ".join(artifact_names[:80])
        prompt = (
            "You are a museum artifact identification system. "
            "Identify which artifact from the SUPPORTED LIST best matches this image. "
            f"SUPPORTED ARTIFACTS: {names_list}\n\n"
            'Respond with JSON only: {"artifact_name": "<exact name from list or UNKNOWN>", "confidence": 0.0-1.0}\n'
            "If uncertain or not in list, use UNKNOWN. Do not invent names."
        )
        try:
            response = self._client.chat.completions.create(
                model=GROQ_VISION_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                    ],
                }],
                max_tokens=256,
                temperature=0.1,
            )
            text = response.choices[0].message.content or ""
            return self._parse_identification(text)
        except Exception as e:
            return {"artifact_name": "UNKNOWN", "confidence": 0.0, "error": str(e)}

    def _parse_identification(self, text: str) -> dict[str, Any]:
        clean_text = re.sub(r"```(?:json)?", "", text).strip()
        try:
            match = re.search(r"\{[^}]+\}", clean_text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                name = str(data.get("artifact_name", "UNKNOWN")).strip().strip('"').strip("'")
                try:
                    conf = float(data.get("confidence", 0.8))
                except (ValueError, TypeError):
                    conf = 0.8
                return {"artifact_name": name, "confidence": conf}
        except (json.JSONDecodeError, ValueError):
            pass
        for line in clean_text.split("\n"):
            if "artifact" in line.lower() and ":" in line:
                name = line.split(":", 1)[1].strip().strip('"').strip("'").strip("`")
                return {"artifact_name": name, "confidence": 0.6}
        return {"artifact_name": "UNKNOWN", "confidence": 0.0}

    def generate_response(
        self,
        user_query: str,
        artifact_name: str | None,
        sqlite_facts: dict[str, Any],
        ir_facts: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.available:
            return self._fallback_response(user_query, artifact_name, sqlite_facts, ir_facts, sources)

        context_parts = []
        if artifact_name:
            context_parts.append(f"Current artifact: {artifact_name}")
        if sqlite_facts:
            context_parts.append("Verified database facts:\n" + json.dumps(sqlite_facts, indent=2))
        if ir_facts:
            context_parts.append("Retrieved evidence:\n" + "\n".join(f"- {f}" for f in ir_facts))
        if sources:
            context_parts.append("Sources:\n" + "\n".join(f"- {s.get('title', 'Unknown')}" for s in sources))

        verified_context = "\n\n".join(context_parts) or "No verified information available."

        prompt = f"""You are a knowledgeable museum guide. Generate a concise, engaging response.

RULES:
- Use ONLY the verified context below. Do NOT invent museum metadata or facts.
- If evidence is insufficient, clearly say you could not find enough information.
- Be warm and educational like a museum docent.
- Keep response under 150 words.

VERIFIED CONTEXT:
{verified_context}

VISITOR QUESTION: {user_query}

Museum guide response:"""

        try:
            response = self._client.chat.completions.create(
                model=GROQ_TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3,
            )
            answer = (response.choices[0].message.content or "").strip()
            return {"answer": answer, "generated_by": "groq"}
        except Exception as e:
            fallback = self._fallback_response(user_query, artifact_name, sqlite_facts, ir_facts, sources)
            fallback["error"] = str(e)
            return fallback

    def _fallback_response(
        self,
        user_query: str,
        artifact_name: str | None,
        sqlite_facts: dict[str, Any],
        ir_facts: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        parts = []
        if artifact_name:
            parts.append(f"Regarding {artifact_name}:")
        if sqlite_facts:
            for k, v in sqlite_facts.items():
                if v and k not in ("artifact_id", "artist_id", "period_id", "gallery_id"):
                    parts.append(f"{k.replace('_', ' ').title()}: {v}")
        if ir_facts:
            parts.extend(ir_facts[:2])
        if not parts:
            return {
                "answer": "I couldn't find enough information in the museum knowledge base to answer that question.",
                "generated_by": "fallback",
            }
        return {"answer": " ".join(parts), "generated_by": "fallback"}
