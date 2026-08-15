"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATASET_DIR = PROJECT_ROOT / "dataset"
DB_PATH = BASE_DIR / "database" / "museum.db"
DOCUMENTS_DIR = DATASET_DIR / "documents"
IMAGES_DIR = DATASET_DIR / "images"
UPLOADS_DIR = BASE_DIR / "uploads"
INDEX_DIR = BASE_DIR / "ir" / "indexes"

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# GroqCloud
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "llama-3.2-90b-vision-preview")
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile")

# Upload limits
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}

# IR
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "5"))
TFIDF_TOP_K = int(os.getenv("TFIDF_TOP_K", "5"))

# NLP
SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")
INTENT_MODEL_PATH = BASE_DIR / "nlp" / "models" / "intent_classifier.joblib"

# QA
QA_MODEL_NAME = os.getenv("QA_MODEL_NAME", "distilbert-base-cased-distilled-squad")

# Ensure directories exist
for d in [UPLOADS_DIR, INDEX_DIR, BASE_DIR / "nlp" / "models"]:
    d.mkdir(parents=True, exist_ok=True)
