"""Benchmark evaluation script for AI Museum Guide NLP/IR subsystems."""
import json
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
TESTSET_PATH = PROJECT_ROOT / "dataset" / "qa" / "museum_qa_testset.json"

sys.path.insert(0, str(BACKEND_DIR))

from database.connection import get_connection
from database.queries import MuseumQueries
from dialogue.manager import DialogueManager
from evaluation.metrics import (
    accuracy,
    exact_match,
    mrr,
    precision_at_k,
    precision_recall_f1,
    recall_at_k,
    token_f1,
)
from ir.retriever import DocumentIndex
from nlp.entity_extractor import extract_entities
from nlp.intent_classifier import TRAINING_DATA, classify_intent
from nlp.slot_filling import fill_slots
from qa.factoid import extract_factoid


def evaluate_intent_classifier():
    print("\n==========================================")
    print("1. INTENT CLASSIFICATION EVALUATION")
    print("==========================================")
    y_true, y_pred = [], []
    for text, label in TRAINING_DATA:
        y_true.append(label)
        pred = classify_intent(text)["intent"]
        y_pred.append(pred)

    metrics = precision_recall_f1(y_true, y_pred)
    print(f"Total Evaluation Samples: {len(y_true)}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1 Score: {metrics['macro_f1']:.4f}")
    return metrics


def evaluate_ir_and_qa(testset, index: DocumentIndex):
    print("\n==========================================")
    print("2. INFORMATION RETRIEVAL (BM25 vs TF-IDF)")
    print("==========================================")
    
    bm25_p3, bm25_r3, bm25_mrr_list = [], [], []
    tfidf_p3, tfidf_r3, tfidf_mrr_list = [], [], []
    em_scores, f1_scores = [], []

    for item in testset:
        query = item["question"]
        target_chunk = item.get("target_chunk_id")
        rel_set = {target_chunk} if target_chunk else set()

        # BM25
        bm25_res = index.search_bm25(query, top_k=3)
        bm25_ids = [r.chunk_id for r in bm25_res]
        if rel_set:
            bm25_p3.append(precision_at_k(rel_set, bm25_ids, k=3))
            bm25_r3.append(recall_at_k(rel_set, bm25_ids, k=3))
            bm25_mrr_list.append(mrr(rel_set, bm25_ids))

        # TF-IDF
        tfidf_res = index.search_tfidf(query, top_k=3)
        tfidf_ids = [r.chunk_id for r in tfidf_res]
        if rel_set:
            tfidf_p3.append(precision_at_k(rel_set, tfidf_ids, k=3))
            tfidf_r3.append(recall_at_k(rel_set, tfidf_ids, k=3))
            tfidf_mrr_list.append(mrr(rel_set, tfidf_ids))

        # Factoid Extraction
        passages = [r.text for r in bm25_res]
        if passages:
            extracted = extract_factoid(query, passages)
            pred_ans = extracted["answer"]
            exp_ans = item["expected_factoid"]
            em_scores.append(exact_match(pred_ans, exp_ans))
            f1_scores.append(token_f1(pred_ans, exp_ans))

    print(f"BM25  -> Precision@3: {sum(bm25_p3)/len(bm25_p3):.4f} | Recall@3: {sum(bm25_r3)/len(bm25_r3):.4f} | MRR: {sum(bm25_mrr_list)/len(bm25_mrr_list):.4f}")
    print(f"TFIDF -> Precision@3: {sum(tfidf_p3)/len(tfidf_p3):.4f} | Recall@3: {sum(tfidf_r3)/len(tfidf_r3):.4f} | MRR: {sum(tfidf_mrr_list)/len(tfidf_mrr_list):.4f}")

    print("\n==========================================")
    print("3. LOCAL FACTOID QA EXTRACTION")
    print("==========================================")
    avg_em = sum(em_scores) / len(em_scores) if em_scores else 0.0
    avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
    print(f"Exact Match (EM): {avg_em:.4f}")
    print(f"Token F1 Score  : {avg_f1:.4f}")


def evaluate_dialogue():
    print("\n==========================================")
    print("4. MULTI-TURN DIALOGUE MANAGEMENT")
    print("==========================================")
    conn = get_connection()
    queries = MuseumQueries(conn)
    dialogue = DialogueManager()
    sid = dialogue.create_session()
    gazetteer = {
        "ARTIFACT": queries.get_all_artifact_names(),
        "ARTIST": queries.get_all_artist_names(),
        "HISTORICAL_PERIOD": queries.get_all_period_names(),
        "GALLERY": queries.get_all_gallery_names(),
        "EXHIBITION": queries.get_all_exhibition_names(),
    }

    turns = [
        ("Tell me about The Thinker.", "ART001"),
        ("Who created it?", "ART001"),
        ("Where is it?", "ART001"),
        ("What other works did he create?", "ARTIST001"),
        ("Which one is the oldest?", "ARTIST001")
    ]

    successes = 0
    for q, expected in turns:
        state = dialogue.get_state(sid)
        intent = classify_intent(q)["intent"]
        entities = extract_entities(q, gazetteer)
        slots = fill_slots(q, intent, entities, state, queries)
        if slots.get("artifact_id"):
            art = queries.get_artifact_by_id(slots["artifact_id"])
            if art:
                dialogue.set_artifact_context(sid, art)
        dialogue.update_state(sid, intent=intent, query=q, artist_id=slots.get("artist_id"))
        
        cur_state = dialogue.get_state(sid)
        if cur_state.get("current_artifact") == expected or cur_state.get("current_artist") == expected:
            successes += 1

    conn.close()
    acc = successes / len(turns)
    print(f"Multi-Turn Dialogue Context Resolution Accuracy: {acc * 100:.1f}% ({successes}/{len(turns)} turns)")


def run_all_evaluations():
    start_time = time.time()
    print("Starting Comprehensive AI Museum Evaluation...")
    
    with open(TESTSET_PATH, "r", encoding="utf-8") as f:
        testset = json.load(f)

    evaluate_intent_classifier()
    
    index = DocumentIndex()
    if not index.load():
        conn = get_connection()
        queries = MuseumQueries(conn)
        index.build(queries.get_document_chunks())
        conn.close()
        
    evaluate_ir_and_qa(testset, index)
    evaluate_dialogue()

    total_latency = (time.time() - start_time) * 1000
    print("\n==========================================")
    print(f"EVALUATION COMPLETE IN {total_latency:.1f} ms")
    print("==========================================")


if __name__ == "__main__":
    run_all_evaluations()
