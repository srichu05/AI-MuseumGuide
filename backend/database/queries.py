"""Structured database query layer."""
from __future__ import annotations

import sqlite3
from typing import Any


class MuseumQueries:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _fetchone_dict(self, query: str, params: tuple = ()) -> dict[str, Any] | None:
        row = self.conn.execute(query, params).fetchone()
        return dict(row) if row else None

    def _fetchall_dicts(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_artifact_by_id(self, artifact_id: str) -> dict[str, Any] | None:
        return self._fetchone_dict(
            """
            SELECT a.*, ar.name AS artist_name, ar.artist_id,
                   p.name AS period_name, p.period_id,
                   g.name AS gallery_name, g.floor, g.location AS gallery_location
            FROM artifacts a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            LEFT JOIN historical_periods p ON a.period_id = p.period_id
            LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
            WHERE a.artifact_id = ?
            """,
            (artifact_id,),
        )

    def get_artifact_by_name(self, name: str) -> dict[str, Any] | None:
        if not name or not name.strip():
            return None
        raw_name = name.strip()
        # Clean noise words
        import re
        clean_name = re.sub(r"\b(artifact|painting|sculpture|piece|artwork|statue|work)\b", "", raw_name, flags=re.IGNORECASE).strip()
        if not clean_name:
            clean_name = raw_name

        rec = self._fetchone_dict(
            """
            SELECT a.*, ar.name AS artist_name, ar.artist_id,
                   p.name AS period_name, p.period_id,
                   g.name AS gallery_name, g.floor, g.location AS gallery_location
            FROM artifacts a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            LEFT JOIN historical_periods p ON a.period_id = p.period_id
            LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
            WHERE LOWER(a.name) = LOWER(?) OR LOWER(a.name) = LOWER(?)
            """,
            (raw_name, clean_name),
        )
        if rec:
            return rec

        # Fallback to LIKE match
        rec = self._fetchone_dict(
            """
            SELECT a.*, ar.name AS artist_name, ar.artist_id,
                   p.name AS period_name, p.period_id,
                   g.name AS gallery_name, g.floor, g.location AS gallery_location
            FROM artifacts a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            LEFT JOIN historical_periods p ON a.period_id = p.period_id
            LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
            WHERE LOWER(a.name) LIKE LOWER(?) OR LOWER(?) LIKE LOWER('%' || a.name || '%')
            ORDER BY LENGTH(a.name) ASC
            """,
            (f"%{clean_name}%", clean_name),
        )
        if rec:
            return rec

        # Token/keyword overlap fallback (e.g. "Gold Mask of Tutankhamun" -> matches "Mask of Tutankhamun")
        import re
        tokens = [t.lower() for t in re.findall(r"\w+", raw_name) if len(t) > 3 and t.lower() not in {"gold", "mask", "bust", "statue", "painting", "sculpture"}]
        for token in tokens:
            rec = self._fetchone_dict(
                """
                SELECT a.*, ar.name AS artist_name, ar.artist_id,
                       p.name AS period_name, p.period_id,
                       g.name AS gallery_name, g.floor, g.location AS gallery_location
                FROM artifacts a
                LEFT JOIN artists ar ON a.artist_id = ar.artist_id
                LEFT JOIN historical_periods p ON a.period_id = p.period_id
                LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
                WHERE LOWER(a.name) LIKE LOWER(?)
                ORDER BY LENGTH(a.name) ASC
                """,
                (f"%{token}%",),
            )
            if rec:
                return rec

        return None

    def list_artifacts(
        self,
        period_id: str | None = None,
        artist_id: str | None = None,
        gallery_id: str | None = None,
        artifact_type: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        clauses = ["1=1"]
        params: list[Any] = []
        if period_id:
            clauses.append("a.period_id = ?")
            params.append(period_id)
        if artist_id:
            clauses.append("a.artist_id = ?")
            params.append(artist_id)
        if gallery_id:
            clauses.append("a.gallery_id = ?")
            params.append(gallery_id)
        if artifact_type:
            clauses.append("LOWER(a.type) = LOWER(?)")
            params.append(artifact_type)
        if search:
            clauses.append("(a.name LIKE ? OR a.description LIKE ? OR ar.name LIKE ?)")
            like = f"%{search}%"
            params.extend([like, like, like])
        params.extend([limit, offset])
        return self._fetchall_dicts(
            f"""
            SELECT a.*, ar.name AS artist_name, p.name AS period_name,
                   g.name AS gallery_name, g.floor
            FROM artifacts a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            LEFT JOIN historical_periods p ON a.period_id = p.period_id
            LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
            WHERE {' AND '.join(clauses)}
            ORDER BY a.name
            LIMIT ? OFFSET ?
            """,
            tuple(params),
        )

    def get_artist_by_id(self, artist_id: str) -> dict[str, Any] | None:
        return self._fetchone_dict("SELECT * FROM artists WHERE artist_id = ?", (artist_id,))

    def get_artist_by_name(self, name: str) -> dict[str, Any] | None:
        return self._fetchone_dict(
            "SELECT * FROM artists WHERE LOWER(name) = LOWER(?)", (name.strip(),)
        )

    def get_other_works_by_artist(self, artist_id: str, exclude_artifact_id: str | None = None) -> list[dict[str, Any]]:
        if exclude_artifact_id:
            return self._fetchall_dicts(
                """
                SELECT artifact_id, name, year, type, image_path
                FROM artifacts
                WHERE artist_id = ? AND artifact_id != ?
                ORDER BY year
                """,
                (artist_id, exclude_artifact_id),
            )
        return self._fetchall_dicts(
            """
            SELECT artifact_id, name, year, type, image_path
            FROM artifacts WHERE artist_id = ? ORDER BY year
            """,
            (artist_id,),
        )

    def list_galleries(self) -> list[dict[str, Any]]:
        return self._fetchall_dicts("SELECT * FROM galleries ORDER BY floor, name")

    def list_exhibitions(self) -> list[dict[str, Any]]:
        return self._fetchall_dicts("SELECT * FROM exhibitions ORDER BY start_date DESC")

    def get_exhibitions_for_artifact(self, artifact_id: str) -> list[dict[str, Any]]:
        return self._fetchall_dicts(
            """
            SELECT e.*
            FROM exhibitions e
            JOIN artifact_exhibitions ae ON e.exhibition_id = ae.exhibition_id
            WHERE ae.artifact_id = ?
            """,
            (artifact_id,),
        )

    def get_artifacts_in_gallery(self, gallery_id: str) -> list[dict[str, Any]]:
        return self._fetchall_dicts(
            """
            SELECT a.artifact_id, a.name, a.year, a.type, a.image_path, ar.name AS artist_name
            FROM artifacts a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            WHERE a.gallery_id = ?
            ORDER BY a.name
            """,
            (gallery_id,),
        )

    def get_all_artifact_names(self) -> list[str]:
        rows = self.conn.execute("SELECT name FROM artifacts ORDER BY name").fetchall()
        return [r["name"] for r in rows]

    def get_all_artist_names(self) -> list[str]:
        rows = self.conn.execute("SELECT name FROM artists ORDER BY name").fetchall()
        return [r["name"] for r in rows]

    def get_all_period_names(self) -> list[str]:
        rows = self.conn.execute("SELECT name FROM historical_periods ORDER BY name").fetchall()
        return [r["name"] for r in rows]

    def get_all_gallery_names(self) -> list[str]:
        rows = self.conn.execute("SELECT name FROM galleries ORDER BY name").fetchall()
        return [r["name"] for r in rows]

    def get_all_exhibition_names(self) -> list[str]:
        rows = self.conn.execute("SELECT name FROM exhibitions ORDER BY name").fetchall()
        return [r["name"] for r in rows]

    def get_document_chunks(self) -> list[dict[str, Any]]:
        return self._fetchall_dicts(
            """
            SELECT c.chunk_id, c.text, c.metadata_json, d.title, d.source_type,
                   d.document_id, d.artifact_id, d.artist_id
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.document_id
            """
        )

    def compare_artifacts(self, artifact_ids: list[str]) -> list[dict[str, Any]]:
        if not artifact_ids:
            return []
        placeholders = ",".join("?" * len(artifact_ids))
        return self._fetchall_dicts(
            f"""
            SELECT a.*, ar.name AS artist_name, p.name AS period_name,
                   g.name AS gallery_name, g.floor
            FROM artifacts a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            LEFT JOIN historical_periods p ON a.period_id = p.period_id
            LEFT JOIN galleries g ON a.gallery_id = g.gallery_id
            WHERE a.artifact_id IN ({placeholders})
            """,
            tuple(artifact_ids),
        )
