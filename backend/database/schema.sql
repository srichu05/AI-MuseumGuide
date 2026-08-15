-- AI Museum Guide SQLite Schema

CREATE TABLE IF NOT EXISTS historical_periods (
    period_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    start_year INTEGER,
    end_year INTEGER,
    description TEXT
);

CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    birth_year INTEGER,
    death_year INTEGER,
    nationality TEXT,
    biography TEXT
);

CREATE TABLE IF NOT EXISTS galleries (
    gallery_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    floor INTEGER,
    location TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS exhibitions (
    exhibition_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT,
    artist_id TEXT REFERENCES artists(artist_id),
    period_id TEXT REFERENCES historical_periods(period_id),
    gallery_id TEXT REFERENCES galleries(gallery_id),
    year INTEGER,
    description TEXT,
    image_path TEXT
);

CREATE TABLE IF NOT EXISTS artifact_exhibitions (
    artifact_id TEXT REFERENCES artifacts(artifact_id),
    exhibition_id TEXT REFERENCES exhibitions(exhibition_id),
    PRIMARY KEY (artifact_id, exhibition_id)
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_type TEXT,
    source_path TEXT,
    artifact_id TEXT REFERENCES artifacts(artifact_id),
    artist_id TEXT REFERENCES artists(artist_id),
    period_id TEXT REFERENCES historical_periods(period_id)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(document_id),
    chunk_index INTEGER,
    text TEXT NOT NULL,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_artifacts_artist ON artifacts(artist_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_period ON artifacts(period_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_gallery ON artifacts(gallery_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
