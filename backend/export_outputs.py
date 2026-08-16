"""Utility script to extract and export AI Museum outputs (artifacts, chat sessions, IR index chunks)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import DB_PATH


def export_all_artifacts_json(output_file: str = "artifacts_export.json"):
    """Export all artifacts and metadata from SQLite DB to JSON."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.artifact_id, a.name, a.type, a.year, a.description,
               ar.name AS artist_name, p.name AS period_name, g.name AS gallery_name
        FROM artifacts a
        LEFT JOIN artists ar ON a.artist_id = ar.artist_id
        LEFT JOIN historical_periods p ON a.period_id = p.period_id
        LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
        ORDER BY a.artifact_id
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    out_path = Path(output_file)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"[+] Successfully exported {len(rows)} artifacts to {out_path.resolve()}")
    return rows


def query_artifact_details(artifact_name_or_id: str):
    """Fetch structured facts and details for a specific artifact."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, ar.name AS artist_name, p.name AS period_name, g.name AS gallery_name
        FROM artifacts a
        LEFT JOIN artists ar ON a.artist_id = ar.artist_id
        LEFT JOIN historical_periods p ON a.period_id = p.period_id
        LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
        WHERE a.artifact_id = ? OR LOWER(a.name) LIKE LOWER(?)
    """, (artifact_name_or_id, f"%{artifact_name_or_id}%"))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    print("=== AI Museum Output Exporter ===")
    export_all_artifacts_json()
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(f"\nQuerying artifact '{query}':")
        res = query_artifact_details(query)
        print(json.dumps(res, indent=2))
