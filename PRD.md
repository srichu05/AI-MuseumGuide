# PRD — AI Museum Guide with Visual Artifact Recognition and Knowledge-Based Conversational QA

## 1. Product Overview

### Product Name
**AI Museum Guide**

### Working Title
**AI Museum Guide with Visual Artifact Recognition and Knowledge-Based Conversational QA**

### Product Type
A multimodal museum information and conversational QA website.

### Core Idea
Build an interactive museum website where a visitor can:

1. Explore a curated digital museum collection.
2. Upload an image of a supported museum artifact/artwork.
3. Have the system identify the likely artifact using GroqCloud multimodal vision.
4. Ask questions about the identified artifact using natural language.
5. Ask follow-up questions while the dialogue manager maintains context.
6. Retrieve factual information from a structured SQLite knowledge base.
7. Retrieve relevant passages from museum documents using traditional Information Retrieval (BM25 / TF-IDF).
8. Extract factoid answers from retrieved text using local NLP/QA methods.
9. Use GroqCloud only for visual identification and final natural-language response generation.
10. Display the answer together with the underlying museum sources/evidence.

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
- Use GroqCloud for multimodal artifact identification.
- Use GroqCloud for final natural-language response generation.
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
          Visual Artifact       Local NLP Pipeline
           Identification             │
                   │             Tokenization
              GroqCloud                 │
                   │             Intent Detection
                   ▼                     │
              Artifact ID         Entity Extraction
                   │                     │
                   └────────┬────────────┘
                            ▼
                  Dialogue Manager
                            │
                     Intent + Slots
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
        Structured Knowledge        Information Retrieval
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
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
                Answer            Sources
```

## Architectural Principle

**Traditional/local NLP and IR must perform the academic NLP tasks.**

GroqCloud is restricted to:

1. **Multimodal visual artifact identification**
2. **Final natural-language response generation**

The local pipeline performs:

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

## Image Processing

- OpenCV for preprocessing
- Optional local pretrained image model/image embeddings for artifact matching
- GroqCloud vision-capable model as the multimodal recognition component/fallback

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

## A. Image Query

Example:

Visitor uploads an image.

```text
Image
  ↓
OpenCV preprocessing
  ↓
GroqCloud Vision
  ↓
Candidate artifact name
  ↓
Validate against SQLite
  ↓
Artifact ID
  ↓
Dialogue state updated
```

If the artifact is not in the supported collection:

```text
artifact = UNKNOWN
```

The system should tell the visitor that the artifact could not be confidently matched to the supported museum collection.

Do not hallucinate an artifact identity.

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

## Image Recognition

Metrics:

- Top-1 Accuracy
- Top-3 Accuracy

If a local image model and GroqCloud recognition are both implemented, compare them.

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

## GroqCloud MAY perform:

### 1. Visual artifact identification

```text
Image → GroqCloud Vision → candidate artifact
```

### 2. Final response generation

```text
Verified facts + retrieved evidence + user query
→ GroqCloud
→ natural-language answer
```

## GroqCloud MUST NOT perform:

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
│   ├── images/
│   ├── documents/
│   └── qa/
│
├── README.md
└── PRD.md
```

The exact folder structure can be adjusted if it improves implementation, but the architectural separation must remain.

---

# 30. Development Priorities

Implement in this order.

## Phase 1 — Project foundation

- repository structure
- Flask backend
- Next.js frontend
- API connection
- SQLite database
- environment configuration

## Phase 2 — Museum data

- artifact records
- artists
- periods
- galleries
- exhibitions
- document corpus
- artifact images

## Phase 3 — NLP

- tokenization
- intent classifier
- entity extraction
- slot filling
- dialogue state

## Phase 4 — IR

- document preprocessing
- BM25
- TF-IDF baseline
- source metadata

## Phase 5 — Factoid QA

- answer extraction
- EM/F1 evaluation

## Phase 6 — GroqCloud

- image identification
- artifact validation
- final response generation

## Phase 7 — Frontend

- museum landing page
- collection
- artifact detail
- image upload
- AI guide
- source display

## Phase 8 — 3D/motion

- React Three Fiber
- Drei
- Motion
- GSAP
- only after functional features work

## Phase 9 — Evaluation

- create test set
- run component metrics
- end-to-end tests
- latency measurements

---

# 31. Definition of Done

The project is complete when a visitor can:

1. Open the museum website.
2. Browse the museum collection.
3. Open an artifact.
4. Upload an image of a supported artifact.
5. Receive an artifact identification.
6. Ask a question about the artifact.
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
18. See evaluation results for the major NLP/IR components.

---

# 32. Final Product Positioning

The final project should be presented as:

> **A multimodal AI Museum Guide that combines computer vision, traditional NLP, information retrieval, structured knowledge querying, extractive factoid QA, dialogue management, and GroqCloud-based natural-language generation to provide grounded conversational access to a curated museum collection.**

The key technical distinction is:

> **The LLM is an augmentation layer, not the NLP pipeline itself.**

The project demonstrates conventional NLP/IR techniques while using a multimodal LLM only where it provides clear value: visual artifact understanding and natural-language response generation.

---

# 33. Agent Instructions

Any coding agent working on this repository must treat this PRD as the primary project specification.

Before changing architecture or introducing a new technology, check this PRD.

Do not replace local NLP/IR components with LLM calls.

Do not expose GroqCloud credentials in the frontend.

Do not create unsupported claims about artifact identity or museum facts.

Prioritize a working end-to-end MVP before adding advanced 3D effects.

The final application must remain a museum knowledge/QA system first and a visual experience second.

The visual design should be impressive, but functionality, correctness, grounded answers, and assignment requirements take priority.
