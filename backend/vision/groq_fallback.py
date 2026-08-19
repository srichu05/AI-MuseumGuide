"""GroqCloud visual fallback service for low-confidence artwork predictions."""
from __future__ import annotations

import base64
import json
import re
from typing import Any

from config import GROQ_API_KEY, GROQ_VISION_MODEL


class GroqFallbackService:
    def __init__(self):
        self._client = None
        if GROQ_API_KEY:
            try:
                from groq import Groq
                self._client = Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")

    @property
    def available(self) -> bool:
        return self._client is not None

    def classify_fallback(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        supported_styles: list[str] | None = None,
        db_queries: Any = None,
    ) -> dict[str, Any]:
        """Called ONLY when CNN prediction confidence is below CNN_CONFIDENCE_THRESHOLD.

        Returns structured fallback result with recognition_source='groq_fallback' and confidence=None.
        """
        if supported_styles is None:
            supported_styles = [
                "Ancient Egypt",
                "Classical Antiquity",
                "Renaissance",
                "Baroque",
                "Neoclassicism",
                "Romanticism",
                "Impressionism",
                "Post-Impressionism",
                "Expressionism",
                "Realism",
                "Surrealism",
                "Modern Art",
                "Contemporary Art",
            ]

        fallback_result: dict[str, Any] = {
            "predicted_style": "Unknown",
            "confidence": None,
            "recognition_source": "groq_fallback",
            "model_version": "cnn-v1",
            "matched_artifact": None,
        }

        if not self.available:
            fallback_result["error"] = "GroqCloud vision client unavailable"
            return fallback_result

        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        styles_str = ", ".join(supported_styles)

        catalog_text = ""
        if db_queries is not None and hasattr(db_queries, "get_all_artifact_names"):
            try:
                artifact_names = db_queries.get_all_artifact_names()
                if artifact_names:
                    catalog_text = f"\nOur museum collection includes the following artifacts:\n{', '.join(artifact_names)}\nIf the image matches one of these works, output its exact title in candidate_artifact_name.\n"
            except Exception:
                pass

        prompt = (
            "You are an expert art historian and museum visual recognition system.\n"
            f"Classify the dominant art style/period of this image from: {styles_str}.\n"
            f"{catalog_text}"
            "Identify:\n"
            "1. Likely art style or historical period\n"
            "2. Specific artwork/artifact title if recognizable (otherwise state UNKNOWN)\n"
            "3. Artist name if confidently identifiable (otherwise state UNKNOWN)\n"
            "Do NOT invent answers if uncertain.\n\n"
            "Respond ONLY with a single JSON object in this exact format:\n"
            '{\n  "predicted_style": "<art style or historical period or Unknown>",\n  "candidate_artifact_name": "<specific artwork title or UNKNOWN>",\n  "candidate_artist_name": "<artist name or UNKNOWN>"\n}'
        )

        try:
            response = self._client.chat.completions.create(
                model=GROQ_VISION_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}},
                    ],
                }],
                max_tokens=1500,
                temperature=0.1,
            )
            raw_text = response.choices[0].message.content or ""
            parsed = self._parse_json(raw_text)

            style = parsed.get("predicted_style", "Unknown").strip()
            for std_style in supported_styles:
                if style.lower() == std_style.lower():
                    style = std_style
                    break

            fallback_result["predicted_style"] = style
            candidate_name = parsed.get("candidate_artifact_name", "UNKNOWN").strip()
            candidate_artist = parsed.get("candidate_artist_name", "UNKNOWN").strip()
            fallback_result["candidate_artist_name"] = candidate_artist

            # Validate candidate artifact against local SQLite museum database
            if candidate_name.upper() != "UNKNOWN" and db_queries is not None:
                artifact = db_queries.get_artifact_by_name(candidate_name)
                if artifact:
                    fallback_result["matched_artifact"] = artifact

        except Exception as e:
            fallback_result["error"] = str(e)

        return fallback_result

    def _parse_json(self, text: str) -> dict[str, Any]:
        """Strip internal reasoning tags (<think>...</think>) and extract JSON object."""
        clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        clean = re.sub(r"```(?:json)?", "", clean).strip()
        try:
            match = re.search(r"\{[^}]+\}", clean, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return {}
