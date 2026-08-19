"""Flask API routes."""
from __future__ import annotations

import uuid

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, UPLOADS_DIR
from vision.preprocess import preprocess_image, validate_image

api = Blueprint("api", __name__)


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@api.route("/artifacts", methods=["GET"])
def list_artifacts():
    q = current_app.queries
    period_id = request.args.get("period_id")
    artist_id = request.args.get("artist_id")
    gallery_id = request.args.get("gallery_id")
    artifact_type = request.args.get("type")
    search = request.args.get("search")
    limit = min(int(request.args.get("limit", 100)), 200)
    offset = int(request.args.get("offset", 0))
    artifacts = q.list_artifacts(period_id, artist_id, gallery_id, artifact_type, search, limit, offset)
    return jsonify({"artifacts": artifacts, "count": len(artifacts)})


@api.route("/artifacts/<artifact_id>", methods=["GET"])
def get_artifact(artifact_id):
    artifact = current_app.queries.get_artifact_by_id(artifact_id)
    if not artifact:
        return jsonify({"error": "Artifact not found"}), 404
    exhibitions = current_app.queries.get_exhibitions_for_artifact(artifact_id)
    related = []
    if artifact.get("artist_id"):
        related = current_app.queries.get_other_works_by_artist(artifact["artist_id"], artifact_id)
    return jsonify({"artifact": artifact, "exhibitions": exhibitions, "related_works": related})


@api.route("/artists/<artist_id>", methods=["GET"])
def get_artist(artist_id):
    artist = current_app.queries.get_artist_by_id(artist_id)
    if not artist:
        return jsonify({"error": "Artist not found"}), 404
    works = current_app.queries.get_other_works_by_artist(artist_id)
    return jsonify({"artist": artist, "works": works})


@api.route("/galleries", methods=["GET"])
def list_galleries():
    galleries = current_app.queries.list_galleries()
    result = []
    for g in galleries:
        artifacts = current_app.queries.get_artifacts_in_gallery(g["gallery_id"])
        result.append({**g, "artifact_count": len(artifacts), "artifacts": artifacts[:6]})
    return jsonify({"galleries": result})


@api.route("/exhibitions", methods=["GET"])
def list_exhibitions():
    return jsonify({"exhibitions": current_app.queries.list_exhibitions()})


@api.route("/search", methods=["POST"])
def search():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    method = data.get("method", "bm25")
    top_k = min(int(data.get("top_k", 5)), 20)
    if not query:
        return jsonify({"error": "Query required"}), 400
    index = current_app.index
    if method == "tfidf":
        results = index.search_tfidf(query, top_k)
    else:
        results = index.search_bm25(query, top_k)
    return jsonify({
        "query": query,
        "method": method,
        "results": [
            {"chunk_id": r.chunk_id, "text": r.text[:500], "score": r.score, "title": r.title, "source_type": r.source_type}
            for r in results
        ],
    })


@api.route("/identify", methods=["POST"])
def identify():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    file = request.files["image"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    raw = file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        return jsonify({"error": f"File exceeds {MAX_UPLOAD_BYTES // (1024*1024)}MB limit"}), 400

    valid, err = validate_image(raw)
    if not valid:
        return jsonify({"error": err}), 400

    processed, mime = preprocess_image(raw)
    safe_name = secure_filename(file.filename)
    upload_path = UPLOADS_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    upload_path.write_bytes(processed)

    # Route through Vision Router (CNN first, Groq fallback if confidence < CNN_CONFIDENCE_THRESHOLD)
    vision_router = getattr(current_app, "vision_router", None)
    if vision_router:
        result = vision_router.route_and_identify(processed, mime_type=mime, db_queries=current_app.queries)
    else:
        from vision.vision_router import VisionRouter
        router = VisionRouter()
        result = router.route_and_identify(processed, mime_type=mime, db_queries=current_app.queries)

    artifact = result.get("matched_artifact")

    session_id = request.form.get("session_id") or current_app.dialogue.create_session()
    if artifact:
        current_app.dialogue.set_artifact_context(session_id, artifact)

    return jsonify({
        "status": "identified" if artifact else "classified",
        "session_id": session_id,
        "predicted_style": result.get("predicted_style"),
        "confidence": result.get("confidence"),
        "recognition_source": result.get("recognition_source"),
        "model_version": result.get("model_version", "cnn-v1"),
        "raw_probabilities": result.get("raw_probabilities"),
        "artifact": artifact,
        "identification": result,
    })


@api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or data.get("message") or "").strip()
    if not query:
        return jsonify({"error": "Query required"}), 400

    session_id = data.get("session_id")
    if not session_id:
        session_id = current_app.dialogue.create_session()

    artifact_id = data.get("artifact_id")
    if artifact_id:
        artifact = current_app.queries.get_artifact_by_id(artifact_id)
        if artifact:
            current_app.dialogue.set_artifact_context(session_id, artifact)

    result = current_app.chat_service.process(session_id, query)
    return jsonify(result)


@api.route("/query", methods=["POST"])
def query_endpoint():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Query required"}), 400
    session_id = data.get("session_id") or current_app.dialogue.create_session()
    result = current_app.chat_service.process(session_id, query)
    return jsonify(result)
