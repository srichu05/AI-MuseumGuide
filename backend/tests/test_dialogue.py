"""Automated test suite for multi-turn dialogue state management."""
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from database.connection import get_connection
from database.queries import MuseumQueries
from dialogue.manager import DialogueManager
from nlp.entity_extractor import extract_entities
from nlp.intent_classifier import classify_intent
from nlp.slot_filling import fill_slots


class TestMultiTurnDialogue(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection()
        self.queries = MuseumQueries(self.conn)
        self.dialogue = DialogueManager()
        self.session_id = self.dialogue.create_session()
        self.gazetteer = {
            "ARTIFACT": self.queries.get_all_artifact_names(),
            "ARTIST": self.queries.get_all_artist_names(),
            "HISTORICAL_PERIOD": self.queries.get_all_period_names(),
            "GALLERY": self.queries.get_all_gallery_names(),
            "EXHIBITION": self.queries.get_all_exhibition_names(),
        }

    def tearDown(self):
        self.conn.close()

    def process_turn(self, query: str):
        state = self.dialogue.get_state(self.session_id)
        intent_res = classify_intent(query)
        intent = intent_res["intent"]
        entities = extract_entities(query, self.gazetteer)
        slots = fill_slots(query, intent, entities, state, self.queries)
        
        # Update dialogue state
        if slots.get("artifact_id"):
            art = self.queries.get_artifact_by_id(slots["artifact_id"])
            if art:
                self.dialogue.set_artifact_context(self.session_id, art)
        self.dialogue.update_state(
            self.session_id,
            intent=intent,
            query=query,
            artist_id=slots.get("artist_id"),
        )
        return intent, slots, self.dialogue.get_state(self.session_id)

    def test_5_turn_thinker_sequence(self):
        # Turn 1: Tell me about The Thinker
        intent1, slots1, state1 = self.process_turn("Tell me about The Thinker.")
        self.assertEqual(slots1["artifact_id"], "ART001")
        self.assertEqual(state1["current_artifact"], "ART001")
        self.assertEqual(state1["current_artist"], "ARTIST001")

        # Turn 2: Who created it?
        intent2, slots2, state2 = self.process_turn("Who created it?")
        self.assertEqual(intent2, "GET_CREATOR")
        self.assertEqual(slots2["artifact_id"], "ART001")

        # Turn 3: Where is it?
        intent3, slots3, state3 = self.process_turn("Where is it?")
        self.assertEqual(intent3, "GET_LOCATION")
        self.assertEqual(slots3["artifact_id"], "ART001")

        # Turn 4: What other works did he create?
        intent4, slots4, state4 = self.process_turn("What other works did he create?")
        self.assertEqual(intent4, "GET_OTHER_WORKS")
        self.assertEqual(slots4["artist_id"], "ARTIST001")

        # Turn 5: Which one is the oldest?
        intent5, slots5, state5 = self.process_turn("Which one is the oldest?")
        self.assertEqual(intent5, "GET_OTHER_WORKS")
        self.assertEqual(slots5["artist_id"], "ARTIST001")


if __name__ == "__main__":
    unittest.main()
