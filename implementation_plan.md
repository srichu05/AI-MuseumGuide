# Implementation Plan — AI Museum Guide

This implementation plan outlines the steps required to complete the **AI Museum Guide with Visual Artifact Recognition and Knowledge-Based Conversational QA** according to `PRD.md` and the user specification.

The project is an academic NLP/IR application where **local NLP/IR handles all analytical tasks** (intent classification, entity extraction, slot filling, dialogue state tracking, database queries, BM25 retrieval, factoid extraction, evaluation), while **GroqCloud is strictly restricted** to visual artifact identification and final natural-language response generation.

---

## Audit & Current State Checklist

### 1. COMPLETE
- **Flask Backend Architecture**: Modular structure with Flask CORS, blueprints in `backend/api/routes.py`, configuration in `backend/config.py`, and entry point in `backend/app.py`.
- **GroqCloud API Client (`backend/llm/groq_client.py`)**: Strictly scoped client for visual identification (JSON-enforced artifact matching against closed collection) and final grounded natural language generation.
- **SQLite Database Layer (`backend/database/`)**: Full schema (`schema.sql`) covering `artifacts`, `artists`, `historical_periods`, `galleries`, `exhibitions`, `artifact_exhibitions`, `documents`, and `document_chunks`.
- **Image Preprocessing (`backend/vision/preprocess.py`)**: OpenCV image resizing, color balance, and validation before sending to Groq Vision.
- **End-to-End Chat Service (`backend/services/chat_service.py`)**: Pipeline routing query through local NLP, structured SQL queries, BM25 retrieval, extractive QA, and Groq response generation.
- **Next.js 14 Frontend Structure (`frontend/`)**: Routes for `/` (Home), `/collection`, `/collection/[id]`, `/gallery`, `/guide`, `/about`.
- **Evaluation Metrics Module (`backend/evaluation/metrics.py`)**: Functions for accuracy, precision/recall/F1, P@K, R@K, MRR, Exact Match, and Token F1.

### 2. PARTIALLY COMPLETE
- **Intent Classifier (`backend/nlp/intent_classifier.py`)**: Uses TF-IDF + Logistic Regression and regex fallback, but only has 25 training examples.
- **Entity Extraction & Slot Filling (`backend/nlp/entity_extractor.py`, `slot_filling.py`)**: Gazetteers and spaCy NER exist, but coreference resolution (`this`, `he`, `it`) needs robust word boundary matching and dialogue fallback logic.
- **Dialogue Manager (`backend/dialogue/manager.py`)**: State machine tracks session state, but multi-turn dialogue context across 5+ turn conversations needs thorough test suite and refinement.
- **Information Retrieval (`backend/ir/retriever.py`)**: BM25 primary and TF-IDF baseline exist, but document corpus chunking currently generates only 1 single chunk per document.
- **Extractive Factoid QA (`backend/qa/factoid.py`)**: Hugging Face pipeline integration with keyword fallback exists, but requires proper evaluation datasets.
- **3D Hero Scene (`frontend/components/three/HeroScene.tsx`)**: Simple floating sphere with distort material. Functional, but needs enhancement into a museum pedestal/artifact showcase.

### 3. BROKEN
- **Artifact Images Strategy**: Seed script creates database entries referencing `images/ART001/image_01.jpg` which do not exist on disk. Frontend (`frontend/lib/api.ts`) defaults to random Unsplash stock photos, presenting unrelated pictures for known masterpieces (e.g. Mona Lisa, The Thinker).
- **Document Segmentation**: `seed.py` creates 1 chunk per document instead of breaking long text into multiple meaningful chunks with complete source metadata (`chunk_id`, `document_id`, `title`, `source_type`, `artifact_id`, `artist_id`, `period_id`).

### 4. MISSING
- **Controlled Museum Image Dataset**: Local static image assets for all 60 seeded artifacts placed in `frontend/public/artifacts/` (and synced with `dataset/images/`) matching the exact artwork names.
- **Comprehensive Evaluation Benchmark Suite**: Test datasets in `dataset/qa/` and script `backend/evaluation/run_eval.py` to evaluate Intent, Entity/Slot, IR (P@K, R@K, MRR), Factoid QA (EM, Token F1), Groq Vision Top-1/Top-3, and Dialogue task success.
- **Groq Vision Model Verification**: Verification and fallback handling for current GroqCloud vision models (e.g., `llama-3.2-11b-vision-preview` / `llama-3.2-90b-vision-instruct`).
- **Enhanced Frontend UI & Rich Interactive Features**: Filtering by artist, period, gallery, and type on `/collection`, rich metadata on `/collection/[id]`, source attribution badges in `/guide`, and responsive design polish.

---

## User Review Required

> [!IMPORTANT]
> **GroqCloud API Key & Model Availability**
> GroqCloud API key is managed via `GROQ_API_KEY` in `backend/.env`. We will ensure the model config points to currently supported GroqCloud Vision & Text models (`llama-3.2-11b-vision-preview` / `llama-3.2-90b-vision-preview` / `llama-3.3-70b-versatile`) with graceful fallback to local facts when the key is missing or offline.

> [!NOTE]
> **Controlled Artifact Image Strategy**
> We will curate clean, public domain image assets for all 60 seeded artifacts (e.g. The Thinker, Mona Lisa, David, Starry Night, Bust of Nefertiti, Girl with a Pearl Earring, etc.) stored in `frontend/public/artifacts/` and `dataset/images/`. Every artifact in the museum will display its authentic image.

---

## Proposed Changes

### Phase 1: Database, Controlled Image Dataset & Multi-Chunk Document Corpus

#### [MODIFY] [backend/database/seed.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/database/seed.py)
- Update seed data so `image_path` points to `/artifacts/<artifact_id>.jpg`.
- Enhance document generation to split text into multiple meaningful chunks (2-4 chunks per document) retaining full metadata (`chunk_id`, `document_id`, `title`, `source_type`, `artifact_id`, `artist_id`, `period_id`, `section`).

#### [NEW] `frontend/public/artifacts/` & `dataset/images/`
- Download/generate authentic high-quality public domain image assets for all 60 seeded artifacts (e.g. `ART001.jpg` through `ART060.jpg`).

---

### Phase 2: NLP Pipeline & Dialogue Management

#### [MODIFY] [backend/nlp/intent_classifier.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/nlp/intent_classifier.py)
- Expand `TRAINING_DATA` from 25 examples to 200+ realistic paraphrases covering all 14 intents (`GREETING`, `GET_ARTIFACT_INFO`, `GET_CREATOR`, `GET_LOCATION`, `GET_PERIOD`, `GET_YEAR`, `GET_HISTORY`, `GET_DESCRIPTION`, `GET_OTHER_WORKS`, `GET_EXHIBITION`, `GET_GALLERY`, `COMPARE_ARTIFACTS`, `HELP`, `UNKNOWN`).
- Retain TF-IDF + Logistic Regression / Linear SVM model and regex fallback without using any LLM.

#### [MODIFY] [backend/nlp/slot_filling.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/nlp/slot_filling.py)
- Enhance coreference resolution for pronouns (`this`, `he`, `it`, `that artwork`, `the artist`) using regex word boundary matching and dialogue state context.

#### [MODIFY] [backend/dialogue/manager.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/dialogue/manager.py)
- Ensure session state correctly tracks multi-turn context (`current_artifact`, `current_artist`, `current_period`, `last_intent`) across complex sequences (e.g. Turn 1: "Tell me about The Thinker" -> Turn 2: "Who created it?" -> Turn 3: "Where is it?" -> Turn 4: "What other works did he create?" -> Turn 5: "Which one is the oldest?").

#### [NEW] [backend/tests/test_dialogue.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/tests/test_dialogue.py)
- Automated unit test verifying multi-turn dialogue context persistence without LLM involvement.

---

### Phase 3: Information Retrieval & Factoid QA

#### [MODIFY] [backend/ir/retriever.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/ir/retriever.py)
- Ensure index precomputation on startup and persistent loading from disk.
- Improve BM25 and TF-IDF scoring and metadata extraction per chunk.

#### [MODIFY] [backend/qa/factoid.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/qa/factoid.py)
- Refine extractive QA span selection and score thresholding using Hugging Face extractive QA model with fallback.

---

### Phase 4: GroqCloud Vision & Text Integration Safeguards

#### [MODIFY] [backend/llm/groq_client.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/llm/groq_client.py)
- Update default vision model candidates (`llama-3.2-11b-vision-preview` / `llama-3.2-90b-vision-preview`).
- Enforce strict JSON output parsing and fallback to `UNKNOWN` when confidence is low or artifact is not in the SQLite database.
- Keep prompt strictly instructed to ground responses ONLY in supplied SQLite facts and IR evidence.

---

### Phase 5: Frontend API Integration & Image Handling

#### [MODIFY] [frontend/lib/api.ts](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/frontend/lib/api.ts)
- Update `getArtifactImage(artifact)` to use real local asset path `/artifacts/${artifact.artifact_id}.jpg` with a graceful fallback.
- Ensure API client handles both server-side and client-side fetches cleanly.

#### [MODIFY] [frontend/app/collection/page.tsx](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/frontend/app/collection/page.tsx)
- Add interactive filter controls for Artist, Period, Gallery, Artifact Type, and Search query.

#### [MODIFY] [frontend/app/collection/[id]/page.tsx](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/frontend/app/collection/[id]/page.tsx)
- Enhance artifact detail page with high-res image, detailed metadata grid, exhibitions list, related works by artist, and direct "Ask Museum Guide" CTA.

#### [MODIFY] [frontend/components/three/HeroScene.tsx](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/frontend/components/three/HeroScene.tsx)
- Upgrade the 3D scene to an elegant museum pedestal with subtle lighting and interactive camera response using R3F and Drei.

---

### Phase 6: Comprehensive Benchmark Evaluation Suite

#### [NEW] `dataset/qa/museum_qa_testset.json`
- Ground-truth evaluation dataset containing questions, expected intent, expected entities, target document/passage IDs, expected factoid answers, and target artifact IDs.

#### [NEW] [backend/evaluation/run_eval.py](file:///c:/Users/R/Raghavendra/Downloads/PROJECTS/AI-museum/backend/evaluation/run_eval.py)
- Command-line evaluation script that runs and reports:
  - **Intent Classification**: Accuracy, Precision, Recall, Macro F1
  - **Information Retrieval**: Precision@K, Recall@K, MRR (comparing BM25 vs TF-IDF)
  - **Factoid QA**: Exact Match (EM) and Token-level F1
  - **Dialogue Management**: Context resolution accuracy & task success rate
  - **Vision Identification**: Top-1 and Top-3 accuracy (if images provided)

---

## Verification Plan

### Automated Tests
- Run backend unit and integration tests:
  ```bash
  python -m unittest discover -s backend/tests -p "test_*.py"
  ```
- Run evaluation pipeline:
  ```bash
  python backend/evaluation/run_eval.py
  ```

### Manual & E2E Verification
1. **Backend Health & APIs**:
   - `GET /api/health` -> `{"status": "ok"}`
   - `GET /api/artifacts` -> List of 60 artifacts with valid local image paths
   - `POST /api/identify` -> Test uploading an image of The Thinker or Mona Lisa
   - `POST /api/chat` -> Test multi-turn dialogue (Turn 1: "Tell me about The Thinker" -> Turn 2: "Who created it?" -> Turn 3: "Where is it located?" -> Turn 4: "What other works did he create?")
2. **Frontend Verification**:
   - Build test: `cd frontend && npm run build`
   - Dev server test: `cd frontend && npm run dev`
   - Test UI flow on browser: Navigation, Collection filters, Artifact Detail, Image Drag & Drop in Guide, Chat panel with source citations.
