"""Flask application entry point."""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from api.routes import api
from config import CORS_ORIGINS, DB_PATH
from database.connection import get_connection, init_db
from database.queries import MuseumQueries
from database.seed import seed as seed_database
from dialogue.manager import DialogueManager
from ir.retriever import DocumentIndex
from llm.groq_client import GroqClient
from nlp.intent_classifier import train_classifier
from services.chat_service import ChatService


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=CORS_ORIGINS, supports_credentials=True)

    if not DB_PATH.exists():
        seed_database()

    conn = get_connection()
    queries = MuseumQueries(conn)
    index = DocumentIndex()
    if not index.load():
        chunks = queries.get_document_chunks()
        index.build(chunks)

    train_classifier()

    dialogue = DialogueManager()
    groq = GroqClient()
    chat_service = ChatService(queries, index, dialogue, groq)

    app.queries = queries
    app.index = index
    app.dialogue = dialogue
    app.groq = groq
    app.chat_service = chat_service
    app.db_conn = conn

    @app.route("/")
    def index():
        from flask import jsonify
        return jsonify({
            "name": "AI Museum Guide API Server",
            "status": "online",
            "frontend_url": "http://localhost:3000",
            "health_check": "http://127.0.0.1:5000/api/health",
            "message": "Welcome to the AI Museum Guide API. Visit http://localhost:3000 for the digital museum experience."
        })

    app.register_blueprint(api, url_prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
