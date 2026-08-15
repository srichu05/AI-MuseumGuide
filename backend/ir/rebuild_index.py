"""Rebuild BM25 and TF-IDF document index from SQLite chunks."""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from database.connection import get_connection
from database.queries import MuseumQueries
from ir.retriever import DocumentIndex


def rebuild():
    conn = get_connection()
    queries = MuseumQueries(conn)
    chunks = queries.get_document_chunks()
    print(f"Building IR index for {len(chunks)} document chunks...")
    index = DocumentIndex()
    index.build(chunks)
    conn.close()
    print("Successfully built BM25 & TF-IDF index!")


if __name__ == "__main__":
    rebuild()
