# PRD — AI Museum Guide with CNN-Based Artwork Style Recognition and Knowledge-Based Conversational QA

## 1. Product Overview

### Product Name
**AI Museum Guide**

### Working Title
**AI Museum Guide with CNN-Based Artwork Style Recognition and Knowledge-Based Conversational QA**

### Product Type
A multimodal museum information and conversational QA website.

### Core Idea
Build an interactive museum website where a visitor can:

1. Explore a curated digital museum collection.
2. Upload an artwork image.
3. Preprocess the image and classify its art style using a locally trained CNN.
4. Display the predicted style together with an appropriate confidence/status.
5. Ask questions about the recognized artwork/style using natural language.
6. Ask follow-up questions while the dialogue manager maintains context.
7. Retrieve factual information from a structured SQLite knowledge base.
8. Retrieve relevant passages from museum documents using traditional Information Retrieval (BM25 / TF-IDF).
9. Extract factoid answers from retrieved text using local NLP/QA methods.
10. Use GroqCloud for grounded final natural-language response generation.
11. Display the answer together with the underlying museum sources/evidence.

The current CNN milestone performs **art-style classification**, not individual artwork/artist identification.

### Visual Fallback Policy

The CNN is the primary visual classifier. Its confidence is checked for every prediction.

- **CNN confidence >= 0.80:** accept the CNN prediction and continue with the local museum pipeline.
- **CNN confidence < 0.80:** invoke **GroqCloud Vision as the visual fallback**.
- The `0.80` value is a **prediction-confidence threshold**, not the CNN's overall accuracy.
- The threshold must be configurable so it can be tuned after validation/evaluation.
- If GroqCloud is used as fallback, its returned visual result must still be handled as an uncertain/candidate result and validated against the supported museum knowledge base where applicable.
- The system must not claim certainty when both the CNN and fallback result are uncertain.

The fallback exists to improve robustness for images that the local CNN cannot classify confidently; GroqCloud does not replace CNN training or evaluation.

This is an academic NLP/IR project. The system must demonstrate actual NLP, Information Retrieval, structured knowledge querying, factoid extraction, and dialogue management rather than delegating these tasks to an LLM.

---

# 2. Problem Statement

Museum visitors often have access to information about artifacts, but that information is distributed across:

- artifact metadata,
- artist information,
- historical-period information,
- gallery information,
- exhibition information,
- museum catalogues,
- artist biographies,
- historical documents,
- exhibition guides,
- museum brochures.

A visitor may know what an artifact looks like but not its name, or may know its name but have questions about its creator, location, historical context, or related works.

The goal is to create a multimodal museum guide that connects visual artifact identification with a conventional NLP/IR-based knowledge system.

---

# 3. Goals

## Primary Goals

- Build a visually impressive museum website.
- Support image-based artifact identification.
- Support text-based museum QA.
- Implement local NLP for query analysis.
- Implement intent classification.
- Implement entity extraction.
- Implement slot filling.
- Implement dialogue state management.
- Implement structured database querying using SQLite.
- Implement document retrieval using BM25 and/or TF-IDF.
- Implement factoid extraction from retrieved passages.
- Use a locally trained CNN as the primary visual artwork-style recognition component.
- Use GroqCloud for final natural-language response generation.
- GroqCloud vision may be retained only as an optional fallback/secondary visual component; it must not replace the CNN training/evaluation pipeline.
- Ground generated responses in locally retrieved/verified information.
- Show sources/evidence to the visitor.
- Provide measurable evaluation of individual subsystems and the complete workflow.

## Secondary Goals

- Make the frontend feel like a modern digital museum rather than a generic chatbot.
- Add 3D/motion elements where they improve the museum experience.
- Keep the architecture modular so the backend and frontend can evolve independently.
- Keep the first implementation manageable with a curated dataset.

---

# 4. Non-Goals

The following are explicitly outside the core scope:

- The system does NOT need to identify every artwork in the world.
- The system does NOT need to be a general-purpose ChatGPT replacement.
- The system does NOT need to provide unrestricted internet-based museum knowledge.
- The LLM must NOT perform intent classification.
- The LLM must NOT perform dialogue state tracking.
- The LLM must NOT replace BM25/TF-IDF retrieval.
- The LLM must NOT replace SQLite querying.
- The LLM must NOT be the primary factoid extraction mechanism.
- The LLM must NOT invent museum metadata.
- Do not over-engineer the first version with unnecessary distributed systems, microservices, vector databases, or complex cloud infrastructure.

The first version should focus on a controlled museum collection and demonstrate the required NLP/IR concepts clearly.

---

# 5. Assignment Alignment

The project must satisfy the following expected capabilities:

1. **Retrieve relevant passages for a question**
   - BM25 and/or TF-IDF over a curated museum document corpus.

2. **Extract factoid answers from text**
   - Local extractive QA / NLP methods.

3. **Query structured knowledge sources**
   - SQLite museum database.

4. **Handle simple conversational interactions**
   - Local dialogue manager, intent classification, slot filling, and context tracking.

5. **Evaluate answer quality**
   - Component-level and end-to-end evaluation.

The project should be demonstrable as a conventional NLP/IR system augmented by multimodal AI, not simply as an LLM wrapper.

---

# 6. Final Architecture

```text
                         VISITOR
                            │
                   ┌────────┴────────┐
                   │                 │
                 IMAGE              TEXT
                   │                 │
                   ▼                 ▼
          Image Validation      Local NLP Pipeline
                   │                   │
          Preprocessing               ├─ Tokenization
                   │                   ├─ Intent Detection
                   ▼                   ├─ Entity Extraction
             CNN Classifier            └─ Slot/Context Resolution
                   │
                   ▼
        Predicted Art Style
          + Confidence
                   │
                   └──────────┬──────────────┐
                              ▼              │
                       Dialogue Manager      │
                              │              │
                         Intent + Slots      │
                              │              │
                 ┌────────────┴────────────┐ │
                 │                         │ │
                 ▼                         ▼ ▼
          Structured Knowledge      Information Retrieval
               SQLite                  BM25 / TF-IDF
                 │                         │
                 │                    Museum Documents
                 │                         │
                 └────────────┬────────────┘
                              ▼
                       Factoid Extraction
                              │
                              ▼
                        Verified Facts
                              │
                              ▼
                       GroqCloud LLM API
                              │
                              ▼
                  Natural Language Generation
                         ┌────┴────┐
                         ▼         ▼
                       Answer   Sources
```

## Architectural Principle

**The system uses a locally trained CNN for visual artwork-style recognition and traditional/local NLP and IR for the academic NLP tasks.**

The CNN is responsible for the first visual classification stage:

1. **Artwork image → preprocessing → CNN → predicted art style + confidence**
2. **If confidence >= 0.80 → accept CNN result**
3. **If confidence < 0.80 → invoke GroqCloud Vision fallback**
4. **Validated visual result → museum knowledge/IR pipeline**

GroqCloud is used for:

1. **Visual fallback when CNN confidence is below 0.80**
2. **Final natural-language response generation**

The CNN remains the primary trained/evaluated visual model. GroqCloud fallback must not replace CNN training, testing, or evaluation.

The local pipeline performs:

- image preprocessing for CNN inference,
- CNN artwork-style classification,
- tokenization,
- intent classification,
- entity extraction,
- slot filling,
- dialogue state tracking,
- coreference/context resolution,
- database querying,
- BM25/TF-IDF retrieval,
- factoid extraction,
- evaluation.

---

# 7. Backend Technology Stack

## Programming Language

**Python**

## Web Framework

**Flask**

Flask provides REST-style API endpoints consumed by the frontend.

## NLP

- spaCy
- NLTK
- scikit-learn

## Intent Classification

Preferred baseline:

- TF-IDF vectorization
- Logistic Regression or Linear SVM

A rule-based fallback may be used for very simple intents.

Do not use GroqCloud to classify intents.

## Entity Extraction

- spaCy NER
- custom entity matching/rules for museum-specific entities

Supported entity types may include:

- ARTIFACT
- ARTIST
- HISTORICAL_PERIOD
- GALLERY
- EXHIBITION
- LOCATION

## Slot Filling

Use local Python/NLP logic.

Example dialogue frame:

```python
{
    "current_artifact": "The Thinker",
    "current_artist": "Auguste Rodin",
    "current_period": "Modern",
    "last_intent": "GET_CREATOR",
    "target": "creator"
}
```

## Dialogue Management

Use a local state-machine/frame-based dialogue manager.

It should resolve simple follow-ups such as:

- "Who created it?"
- "Where is it located?"
- "What about its history?"
- "What other works did he create?"
- "Which one is the oldest?"

The dialogue manager should maintain the current artifact, artist, intent, and other relevant slots.

## Information Retrieval

Use:

- BM25
- TF-IDF

Recommended primary retrieval method: BM25.

TF-IDF can be retained as a baseline for evaluation/comparison.

## Factoid Extraction

Use local extractive methods.

Possible implementation:

- Hugging Face extractive QA model
- spaCy NER
- answer-span extraction

The system should retrieve passages first and then extract the relevant answer span.

## Structured Knowledge

**SQLite**

SQLite is sufficient for the initial project because the museum collection is curated and the application is primarily a prototype/academic system.

No PostgreSQL is required for the first version.

## CNN Framework

Preferred first implementation:

- **TensorFlow / Keras**

The first model should be a simple, reproducible CNN baseline. Transfer learning may be introduced only after the baseline has been trained and evaluated.

The CNN module should include:

- dataset verification
- image loading
- preprocessing
- training-only augmentation
- model definition
- training
- validation
- test evaluation
- checkpointing
- model export
- inference
- confidence thresholding
- class-index persistence

## Computer Vision / CNN

- OpenCV or Pillow for image loading and preprocessing
- TensorFlow/Keras or PyTorch for CNN implementation
- Image resizing to the model input size
- Normalization
- Training-time data augmentation
- Dropout / regularization where appropriate
- Softmax classification over the six initial art-style classes
- Model checkpointing and early stopping
- Confusion matrix and Top-1 / Top-3 accuracy evaluation

### Initial CNN Classes

The current dataset prepared for the project contains approximately 3,000 images across six classes:

- Impressionism
- Realism
- Romanticism
- Expressionism
- Post-Impressionism
- Surrealism

The initial target is approximately 500 images per class, split into:

- 70% training
- 15% validation
- 15% test

This CNN recognizes **art style**, not individual artwork identity. Individual artifact identification requires a separately labelled artifact-level dataset and is outside the current CNN milestone.

# Visual Fallback Routing

The visual recognition router follows a confidence-gated strategy.

```text
Artwork image
    ↓
CNN
    ↓
style + confidence
    ↓
confidence >= 0.80?
    ├── YES → use CNN result
    └── NO  → call GroqCloud Vision fallback
```

### Threshold

The initial threshold is:

```text
CNN_CONFIDENCE_THRESHOLD = 0.80
```

This value means **80% model-prediction confidence**, not 80% model accuracy.

The threshold must be configurable through backend configuration/environment settings so it can be changed after empirical evaluation.

### Fallback Requirements

When fallback is triggered:

1. Record that CNN confidence was below the threshold.
2. Send the image to the configured GroqCloud vision-capable model.
3. Request a structured visual result.
4. Distinguish fallback output from CNN output in the API response.
5. Validate any claimed artifact identity against SQLite if an artifact identity is returned.
6. Do not use GroqCloud fallback as evidence that the CNN is accurate.
7. If both systems are uncertain or disagree, return an uncertainty state rather than silently choosing an unsupported identity.

### Why the fallback exists

The fallback handles difficult or out-of-distribution images for which the local CNN is not sufficiently confident. The local CNN remains the primary model and must still be trained and evaluated independently.

## LLM / Multimodal API

**GroqCloud API only**

Use GroqCloud for:

### A. Visual Artifact Identification

Input:
- visitor image
- strict identification prompt

Output should preferably be structured, e.g.:

```json
{
  "artifact_name": "The Thinker"
}
```

If uncertain:

```json
{
  "artifact_name": "UNKNOWN"
}
```

The application must validate the returned artifact against the local SQLite museum collection before using it.

### B. Final Response Generation

GroqCloud receives only verified/retrieved information:

- user query,
- current artifact,
- SQLite facts,
- extracted IR facts,
- source information.

The prompt must instruct the model to use only supplied verified context and avoid unsupported claims.

---

# 8. Backend Working

## A. Image Query / CNN Style Recognition

Example:

Visitor uploads an artwork image.

```text
Image
  ↓
File/type/size validation
  ↓
OpenCV / Pillow preprocessing
  ↓
CNN inference
  ↓
Predicted art style + confidence
  ↓
Is confidence >= 0.80?
  ├── YES → accept CNN result
  │          ↓
  │       museum knowledge/IR
  │
  └── NO  → GroqCloud Vision fallback
             ↓
          candidate visual result
             ↓
          validate against supported knowledge
             ↓
          museum knowledge/IR
```

The CNN is the **primary visual recognition mechanism**. GroqCloud is the **fallback visual recognition mechanism** only when the CNN prediction confidence is below `0.80`.

The API should expose the recognition source, for example:

```json
{
  "predicted_style": "Impressionism",
  "confidence": 0.87,
  "recognition_source": "cnn",
  "model_version": "cnn-v1"
}
```

When fallback is triggered:

```json
{
  "predicted_style": "Impressionism",
  "confidence": null,
  "recognition_source": "groq_fallback"
}
```

The fallback response must not be treated as a measured CNN confidence score. The application should record that the result came from GroqCloud.

The `0.80` threshold must be configurable rather than hard-coded throughout the application.

Example output:

```json
{
  "predicted_style": "Impressionism",
  "confidence": 0.87
}
```

The application must not present a low-confidence prediction as certain. A confidence threshold should be configurable and evaluated during testing.

If the predicted style is outside the supported six-class model or confidence is below the configured threshold:

```text
style = UNKNOWN
```

The system should tell the visitor that the image could not be confidently classified by the current CNN.

Do not invent an artwork identity from a style prediction.

**Important:** The current CNN predicts an art style, not a specific artwork, artist, or artifact. The system must preserve this distinction in the UI and API response.

---

# 9. Text Query Workflow

Example:

> "Who created this?"

### Step 1 — NLP preprocessing

Use spaCy/NLTK.

### Step 2 — Intent classification

Example:

```text
GET_CREATOR
```

### Step 3 — Entity/slot resolution

Resolve:

```text
"this" → current_artifact
```

### Step 4 — Structured query

SQLite:

```sql
SELECT artist, creation_year
FROM artifacts
WHERE artifact_id = ?;
```

### Step 5 — Verified result

Example:

```text
Artist: Auguste Rodin
Year: 1904
```

### Step 6 — GroqCloud generation

GroqCloud turns the verified facts into a natural museum-guide response.

---

# 10. Historical / Knowledge Query Workflow

Example:

> "Tell me about the historical significance of this sculpture."

Pipeline:

```text
User query
    ↓
NLP preprocessing
    ↓
Intent = GET_HISTORICAL_INFO
    ↓
Resolve current artifact
    ↓
BM25 retrieval
    ↓
Top-K museum passages
    ↓
Factoid extraction
    ↓
Verified facts
    ↓
GroqCloud response generation
    ↓
Answer + sources
```

---

# 11. Structured Knowledge Database

Use SQLite.

Suggested tables:

## artifacts

```text
artifact_id
name
type
artist_id
period_id
gallery_id
year
description
image_path
```

## artists

```text
artist_id
name
birth_year
death_year
nationality
biography
```

## historical_periods

```text
period_id
name
start_year
end_year
description
```

## galleries

```text
gallery_id
name
floor
location
description
```

## exhibitions

```text
exhibition_id
name
start_date
end_date
description
```

## artifact_exhibitions

```text
artifact_id
exhibition_id
```

Additional tables can be added only when needed.

---

# 12. Dataset

The first version should use a **controlled museum dataset** rather than attempting universal artifact recognition.

## 12.1 CNN Image Dataset

The current CNN training dataset has already been prepared locally from a WikiArt-derived dataset.

Initial classes:

```text
Impressionism
Realism
Romanticism
Expressionism
Post-Impressionism
Surrealism
```

Target dataset size:

```text
6 classes × approximately 500 images = approximately 3,000 images
```

Split:

```text
Train       ≈ 70%  → 2,100 images
Validation  ≈ 15%  →   450 images
Test        ≈ 15%  →   450 images
```

Expected project structure:

```text
dataset/
└── ai_museum_cnn/
    ├── train/
    │   ├── impressionism/
    │   ├── realism/
    │   ├── romanticism/
    │   ├── expressionism/
    │   ├── post-impressionism/
    │   └── surrealism/
    ├── validation/
    │   └── same six classes
    └── test/
        └── same six classes
```

The dataset is used specifically for **CNN art-style classification**.

The dataset must not be committed to GitHub if its size/licensing makes repository storage inappropriate. Keep the dataset locally and document its source and preparation procedure.

## 12.2 CNN Data Preparation

Before training:

1. Verify class counts.
2. Detect unreadable/corrupt images.
3. Check for obvious duplicates or leakage between splits where practical.
4. Resize images to the selected CNN input resolution.
5. Normalize pixel values.
6. Apply augmentation only to the training set.
7. Keep validation and test preprocessing deterministic.
8. Record the class-to-index mapping.

Example:

```python
class_names = [
    "expressionism",
    "impressionism",
    "post-impressionism",
    "realism",
    "romanticism",
    "surrealism"
]
```

The exact class-index mapping must be stored with the trained model and used consistently during inference.

## 12.3 Existing Museum Dataset

The application may additionally maintain the curated museum metadata/document dataset described below.

Recommended initial scope:

- approximately 50–100 artifacts
- approximately 10–30 artists
- approximately 5–10 historical periods
- approximately 5–10 galleries
- several exhibitions
- artifact images
- artifact descriptions
- artist biographies
- museum catalogues
- historical documents
- exhibition guides
- museum brochures

The dataset can contain well-known public-domain/cultural-heritage artifacts and a curated set of museum-style metadata.

## Image Dataset

Each supported artifact should ideally have multiple images where possible:

```text
dataset/images/
├── ART001/
│   ├── image_01.jpg
│   ├── image_02.jpg
│   └── image_03.jpg
├── ART002/
│   ├── image_01.jpg
│   └── image_02.jpg
```

Multiple views help test robustness.

## Document Dataset

```text
dataset/documents/
├── artifact_catalogues/
├── artist_biographies/
├── historical_documents/
├── exhibition_guides/
└── museum_brochures/
```

Documents should be converted to clean text/paragraph chunks for BM25/TF-IDF.

Each document/chunk should retain metadata such as:

- document title
- source
- artifact_id where applicable
- artist_id where applicable
- page/section if available

This metadata will later be used for source display.

---

# 13. Example Museum Data

Example artifact:

```text
Artifact:
The Thinker

Artist:
Auguste Rodin

Year:
1904

Period:
Modern Sculpture

Gallery:
Gallery 4

Floor:
2
```

Example user interaction:

```text
Visitor uploads image
→ system identifies "The Thinker"

Visitor:
Who created this?

NLP:
Intent = GET_CREATOR
Artifact = The Thinker

SQLite:
Artist = Auguste Rodin
Year = 1904

GroqCloud:
Generate natural response from verified facts.
```

Follow-up:

```text
Visitor:
Where is it?

NLP:
Intent = GET_LOCATION
Artifact = current_artifact

SQLite:
Gallery 4, Floor 2
```

Another follow-up:

```text
Visitor:
Tell me about its historical significance.

NLP:
Intent = GET_HISTORICAL_INFO

BM25:
Retrieve relevant passages.

Factoid extraction:
Extract relevant historical facts.

GroqCloud:
Generate concise grounded response.

UI:
Answer + sources.
```

---

# 14. Suggested Intents

Initial intent set:

```text
GREETING
GET_ARTIFACT_INFO
GET_CREATOR
GET_LOCATION
GET_PERIOD
GET_YEAR
GET_HISTORY
GET_DESCRIPTION
GET_OTHER_WORKS
GET_EXHIBITION
GET_GALLERY
COMPARE_ARTIFACTS
HELP
UNKNOWN
```

The implementation can begin with a smaller subset and expand as the system stabilizes.

---

# 15. Dialogue State

Maintain a conversation state per active session.

Example:

```python
{
    "current_artifact": "ART001",
    "current_artist": "ARTIST001",
    "current_period": "PERIOD001",
    "last_intent": "GET_CREATOR",
    "last_query": "Who created this?"
}
```

The dialogue manager should use this state to resolve simple pronouns/references.

Do not use an LLM for dialogue state tracking.

---

# 16. API Design

Suggested Flask endpoints:

```text
POST /api/identify
POST /api/chat
POST /api/query
GET  /api/artifacts
GET  /api/artifacts/<artifact_id>
GET  /api/artists/<artist_id>
GET  /api/galleries
GET  /api/exhibitions
POST /api/search
GET  /api/sources/<source_id>
```

The exact API design may evolve during implementation, but maintain a clean frontend/backend contract.

---

# 17. Frontend Technology Stack

The frontend should be a modern, scalable React-based application.

## Core

- TypeScript
- React
- Next.js

## Styling

- Tailwind CSS

## UI Components

- shadcn/ui

## 2D Motion

- Motion for React

## 3D

- Three.js
- React Three Fiber
- Drei

## Advanced Animation

- GSAP
- GSAP ScrollTrigger

The frontend must not look like a generic chatbot dashboard.

It should feel like a modern digital museum.

---

# 18. Frontend Visual Direction

Desired visual character:

- premium museum aesthetic
- dark/neutral gallery-inspired palette
- large artwork imagery
- elegant typography
- subtle motion
- smooth page transitions
- restrained 3D effects
- cinematic hero section
- interactive artifact cards
- immersive artifact detail pages
- museum-guide chat panel
- responsive desktop/mobile design

Avoid excessive animation. Animation should support exploration rather than distract from content.

---

# 19. Frontend Pages

## Home

Purpose:

Introduce the digital museum.

Possible elements:

- cinematic hero
- 3D artifact/model
- featured artifacts
- featured exhibition
- "Explore Collection"
- "Identify an Artifact"
- "Ask the Museum Guide"

## Collection

Features:

- artifact grid
- search
- filters
- artifact categories
- historical periods
- artists
- gallery filtering

## Artifact Detail

Display:

- artifact image
- title
- artist
- year
- historical period
- gallery
- description
- related works
- exhibition information
- "Ask about this artifact"

## AI Museum Guide

Features:

- image upload
- drag-and-drop
- image preview
- identification state
- recognized artifact
- confidence/status where appropriate
- conversational QA
- source citations
- conversation history for the active session

## Gallery

Optional immersive view:

- 3D gallery-style environment
- artifact cards
- interactive navigation
- selected artifact information

3D should remain lightweight and optional so it does not hurt performance.

## About

Explain:

- museum collection
- project
- AI system
- NLP/IR methodology
- source/evidence philosophy

---

# 20. AI Interaction UX

Image upload experience:

```text
Upload image
    ↓
Analyzing
    ↓
Identifying
    ↓
Matched artifact
    ↓
Artifact information
    ↓
Ask a question
```

The UI should clearly distinguish:

- visual identification
- verified museum information
- generated explanation
- sources

Never display an uncertain model output as unquestionable fact.

---

# 21. Source Display

Every knowledge-based answer should provide source information when available.

Example:

```text
Answer

The sculpture was created by Auguste Rodin in 1904...

Sources
• Museum Artifact Catalogue
• Artist Biography
• Historical Sculpture Guide
```

Sources must correspond to actual retrieved documents/database records.

Do not invent sources.

---

# 22. Evaluation

Evaluate subsystems independently.

## CNN Image Classification

Metrics:

- Training accuracy
- Validation accuracy
- Test accuracy
- Top-1 Accuracy
- Top-3 Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- Per-class performance
- Training/validation loss curves
- Inference latency

The CNN must be evaluated on the held-out test set.

If an optional GroqCloud vision component is later retained, it may be compared against the CNN, but the CNN remains the primary trained visual classifier for the current milestone.

## Intent Classification

Metrics:

- Accuracy
- Precision
- Recall
- F1-score

## Slot Filling / Entity Extraction

Metrics:

- Precision
- Recall
- F1-score

## Information Retrieval

Metrics:

- Precision@K
- Recall@K
- MRR

Compare BM25 and TF-IDF if both are implemented.

## Factoid Extraction

Metrics:

- Exact Match
- Token-level F1

## Dialogue

Metrics:

- task success rate
- context resolution accuracy

## End-to-End

Metrics:

- answer correctness
- source grounding
- task success
- average latency

---

# 23. Security and Reliability

Implement basic safeguards:

- validate uploaded file types
- limit upload size
- sanitize filenames
- store uploads safely
- do not expose API keys to the frontend
- keep `GROQ_API_KEY` in backend environment variables
- validate GroqCloud artifact names against SQLite
- gracefully handle API failures
- gracefully handle unknown artifacts
- gracefully handle empty retrieval results

Never place the Groq API key in frontend JavaScript.

---

# 24. Error Handling

Examples:

### Unknown artifact

```text
"I couldn't confidently match this image to an artifact in the supported museum collection."
```

### No retrieval result

```text
"I couldn't find enough information in the museum knowledge base to answer that."
```

### GroqCloud unavailable

The system should still provide database/IR results where possible.

### Ambiguous artifact

Display candidate/uncertainty instead of presenting an unsupported exact identity.

---

# 25. Performance Principles

- Cache static museum data.
- Precompute BM25/TF-IDF indexes at startup or during ingestion.
- Avoid rebuilding retrieval indexes for every request.
- Keep image processing lightweight.
- Compress/resize uploaded images before vision API calls.
- Use asynchronous frontend states for API calls.
- Lazy-load 3D assets.
- Lazy-load heavy museum imagery.
- Avoid excessive WebGL effects on mobile.
- Keep API keys server-side.

---

# 26. Code Quality Rules

The coding agent must:

- keep frontend and backend separated
- use clear modules
- avoid monolithic files
- use environment variables for secrets
- use reusable React components
- use TypeScript types/interfaces
- add useful comments only where logic is non-obvious
- avoid duplicated code
- preserve separation between NLP/IR and LLM responsibilities
- avoid unnecessary dependencies
- keep API contracts documented
- provide meaningful error messages

---

# 27. Critical LLM Boundary

This rule is mandatory.

## CNN MAY / MUST perform:

### 1. Artwork style classification

```text
Image → preprocessing → CNN → predicted style + confidence
```

### 2. Visual evaluation

The CNN must be evaluated independently using the held-out test set.

## GroqCloud MAY perform:

### 1. Visual fallback

When the CNN prediction confidence is below `0.80`, GroqCloud Vision may be invoked as the fallback visual recognition component.

```text
CNN confidence < 0.80
        ↓
GroqCloud Vision
        ↓
candidate style/artifact result
        ↓
local validation where applicable
```

### 2. Final response generation

```text
Verified facts + retrieved evidence + user query
→ GroqCloud
→ natural-language answer
```

## GroqCloud MUST NOT perform:

- replacing the CNN as the primary trained visual classifier
- bypassing the CNN confidence-gated fallback policy
- intent classification
- slot filling
- dialogue state tracking
- BM25 retrieval
- TF-IDF retrieval
- database querying
- factoid extraction
- evaluation
- source selection based on unsupported knowledge
- invention of museum metadata

If the coding agent sees an opportunity to use the LLM for one of these tasks, it must preserve the local NLP/IR implementation.

---

# 28. Frontend/Backend Communication

The frontend should communicate with Flask through JSON REST APIs.

Example:

```text
Next.js / React
      ↓
POST /api/identify
      ↓
Flask
      ↓
GroqCloud Vision
      ↓
SQLite validation
      ↓
JSON response
      ↓
React UI
```

Chat:

```text
React
 ↓
POST /api/chat
 ↓
Flask
 ↓
NLP
 ↓
Dialogue Manager
 ↓
SQLite / BM25 / QA
 ↓
GroqCloud generation
 ↓
JSON response
 ↓
React
```

---

# 29. Recommended Project Structure

```text
museum-ai/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── api/
│   ├── nlp/
│   ├── dialogue/
│   ├── ir/
│   ├── qa/
│   ├── vision/
│   ├── llm/
│   ├── database/
│   ├── evaluation/
│   ├── documents/
│   └── uploads/
│
├── frontend/
│   ├── package.json
│   ├── next.config.*
│   ├── app/
│   ├── components/
│   │   ├── museum/
│   │   ├── artifact/
│   │   ├── chat/
│   │   ├── upload/
│   │   ├── gallery/
│   │   └── three/
│   ├── lib/
│   ├── types/
│   └── public/
│       ├── artifacts/
│       ├── models/
│       └── textures/
│
├── dataset/
│   ├── ai_museum_cnn/
│   │   ├── train/
│   │   ├── validation/
│   │   └── test/
│   ├── images/
│   ├── documents/
│   └── qa/

├── cnn/
│   ├── train.py
│   ├── evaluate.py
│   ├── predict.py
│   ├── model/
│   └── class_names.json/
│
├── README.md
└── PRD.md
```

The exact folder structure can be adjusted if it improves implementation, but the architectural separation must remain.

---

# Current CNN Milestone

The current implementation stage is the **CNN visual classification milestone**.

The dataset has already been prepared and placed in the project directory. The next implementation sequence is:

```text
Existing dataset
    ↓
Dataset verification
    ↓
Preprocessing + augmentation
    ↓
CNN baseline
    ↓
Training
    ↓
Validation
    ↓
Test evaluation
    ↓
Save/export model
    ↓
Create local prediction script
    ↓
Integrate CNN inference into Flask
    ↓
Connect prediction to the museum UI
```

The coding agent must not skip directly to GroqCloud integration or advanced frontend work until the CNN baseline has been trained and evaluated.

# 30. Development Priorities

Implement in this order. Existing implementation work may already satisfy portions of earlier phases; the current active milestone is Phase 2.

## Phase 1 — Project foundation

- repository structure
- Flask backend
- Next.js frontend
- API connection
- SQLite database
- environment configuration

## Phase 2 — CNN Visual Recognition — CURRENT MILESTONE

- verify the existing `dataset/ai_museum_cnn` dataset
- verify class counts and split integrity
- detect corrupt/unreadable images
- establish class-to-index mapping
- image preprocessing
- training-only augmentation
- build a CNN baseline
- train on the 6 current art-style classes
- validate during training
- evaluate on the held-out test set
- generate confusion matrix and classification report
- measure inference latency
- save/export the trained model
- save the class mapping and model version
- create a standalone local prediction script
- establish a configurable confidence threshold (initially 0.80)
- implement CNN → GroqCloud fallback routing
- integrate CNN inference and fallback routing into Flask

## Phase 3 — Museum data

- artifact records
- artists
- periods
- galleries
- exhibitions
- document corpus
- museum metadata
- supporting artifact images

## Phase 4 — NLP

- tokenization
- intent classifier
- entity extraction
- slot filling
- dialogue state
- context/coreference handling

## Phase 5 — IR

- document preprocessing
- BM25
- TF-IDF baseline
- source metadata

## Phase 6 — Factoid QA

- answer extraction
- EM/F1 evaluation

## Phase 7 — GroqCloud

- final response generation
- optional multimodal fallback/secondary assistance
- grounded response generation from verified local facts

## Phase 8 — Frontend

- museum landing page
- collection
- artifact detail
- CNN image upload/prediction UI
- AI guide
- source display
- confidence/uncertainty display

## Phase 9 — 3D/motion

- React Three Fiber
- Drei
- Motion
- GSAP
- only after functional features work

## Phase 10 — Evaluation

- create CNN test cases
- run CNN component metrics
- run NLP/IR component metrics
- end-to-end tests
- latency measurements
- compare baseline/model variants where applicable

# 31. Definition of Done

The project is complete when a visitor can:

1. Open the museum website.
2. Browse the museum collection.
3. Open an artifact.
4. Upload an image of a supported artifact.
5. Receive a CNN-based art-style prediction with confidence/status.
6. Ask a question about the recognized artwork/style.
7. Have the local NLP pipeline identify the intent.
8. Have the dialogue manager resolve the current artifact/context.
9. Retrieve structured facts from SQLite where appropriate.
10. Retrieve relevant passages with BM25/TF-IDF where appropriate.
11. Extract factoid information locally.
12. Send verified information to GroqCloud.
13. Receive a natural-language museum-guide response.
14. See supporting sources.
15. Ask follow-up questions without losing basic context.
16. Receive graceful responses when information is unavailable.
17. Use the website on desktop and mobile.
18. See CNN evaluation results including accuracy, F1, confusion matrix, and latency.
19. See evaluation results for the major NLP/IR components.

---

# 32. Final Product Positioning

The final project should be presented as:

> **A multimodal AI Museum Guide that combines CNN-based artwork style recognition, traditional NLP, information retrieval, structured knowledge querying, extractive factoid QA, dialogue management, and GroqCloud-based natural-language generation to provide grounded conversational access to a curated museum collection.**

The key technical distinctions are:

> **The CNN is the primary visual classification model, and the LLM is an augmentation layer rather than the NLP pipeline itself.**

> **The current CNN predicts art style, not individual artwork identity.**

The project demonstrates conventional NLP/IR techniques while using a multimodal LLM only where it provides clear value: visual artifact understanding and natural-language response generation.

---

# 33. Agent Instructions

Any coding agent working on this repository must treat this PRD as the primary project specification.

### Current active task

The current active implementation milestone is **CNN-based artwork style recognition**.

The dataset has already been prepared and placed in:

```text
dataset/ai_museum_cnn/
├── train/
├── validation/
└── test/
```

The dataset contains six initial classes:

```text
Impressionism
Realism
Romanticism
Expressionism
Post-Impressionism
Surrealism
```

The agent must proceed in this order:

```text
Verify dataset
→ preprocess
→ augment training data
→ build CNN baseline
→ train
→ validate
→ evaluate test set
→ save model
→ save class mapping
→ create prediction script
→ integrate CNN into Flask
```

The agent must **not**:

- replace the CNN with GroqCloud vision
- assume the CNN identifies an individual artwork or artist
- train on the test set
- apply random augmentation to validation/test data
- silently change the six-class dataset
- commit the large dataset to GitHub
- expose API keys in the frontend
- skip evaluation before integration

The agent should preserve the distinction between:

```text
CNN prediction = art style
Museum database = curated museum facts
BM25/TF-IDF = document retrieval
Local QA/NLP = factoid extraction and query processing
GroqCloud = final natural-language generation
```

### CNN → GroqCloud Fallback Rule

The visual router must use this policy:

```text
CNN confidence >= 0.80
    → use CNN prediction

CNN confidence < 0.80
    → invoke GroqCloud Vision fallback
```

The `0.80` value is a confidence threshold, not CNN accuracy. Keep it configurable.

The API must identify whether the final visual result came from:

- `cnn`
- `groq_fallback`

Do not call GroqCloud Vision for every image. Do not remove the CNN confidence gate.

Before changing architecture or introducing a new technology, check this PRD.

Do not replace local NLP/IR components with LLM calls.

Do not create unsupported claims about artwork identity or museum facts.

Prioritize a working CNN baseline and end-to-end MVP before adding advanced 3D effects.

The final application must remain a museum knowledge/QA system first and a visual experience second.

The visual design should be impressive, but functionality, correctness, grounded answers, and assignment requirements take priority.
