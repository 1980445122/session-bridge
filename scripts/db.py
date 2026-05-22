"""Session Bridge — SQLite database layer."""
import sqlite3
import os
import json
from datetime import datetime, timezone

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "sessions.db")


def get_db() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            project_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            summary TEXT,
            decisions TEXT,
            current_tasks TEXT,
            key_files TEXT,
            tags TEXT,
            note TEXT,
            raw_snippet TEXT,
            is_cloud_synced INTEGER DEFAULT 0
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
            summary, decisions, current_tasks, key_files, tags, note,
            content='sessions',
            content_rowid='rowid'
        );
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    conn.commit()
    conn.close()


def save_session(session_id: str, project_path: str, summary: str,
                 decisions: str = "", current_tasks: str = "",
                 key_files: str = "", tags: str = "", note: str = "",
                 raw_snippet: str = ""):
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    existing = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if existing:
        conn.execute("""
            UPDATE sessions SET updated_at=?, summary=?, decisions=?,
            current_tasks=?, key_files=?, tags=?, note=?, raw_snippet=?
            WHERE id=?
        """, (now, summary, decisions, current_tasks, key_files, tags, note, raw_snippet, session_id))
    else:
        conn.execute("""
            INSERT INTO sessions (id, project_path, created_at, updated_at, summary,
            decisions, current_tasks, key_files, tags, note, raw_snippet)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, project_path, now, now, summary, decisions,
              current_tasks, key_files, tags, note, raw_snippet))
    conn.commit()
    conn.close()


def list_sessions(limit: int = 10, project_path: str = None) -> list:
    conn = get_db()
    if project_path:
        rows = conn.execute(
            "SELECT id, project_path, created_at, summary, tags, note FROM sessions "
            "WHERE project_path=? ORDER BY created_at DESC LIMIT ?",
            (project_path, limit)).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, project_path, created_at, summary, tags, note FROM sessions "
            "ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session(session_id: str) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def search_sessions(query: str, limit: int = 10) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT s.id, s.project_path, s.created_at, s.summary, s.tags, s.note "
        "FROM sessions s JOIN sessions_fts fts ON s.rowid = fts.rowid "
        "WHERE sessions_fts MATCH ? ORDER BY rank LIMIT ?",
        (query, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_storage_stats() -> dict:
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) as n FROM sessions").fetchone()["n"]
    size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    oldest = conn.execute("SELECT MIN(created_at) as d FROM sessions").fetchone()["d"]
    newest = conn.execute("SELECT MAX(created_at) as d FROM sessions").fetchone()["d"]
    synced = conn.execute("SELECT COUNT(*) as n FROM sessions WHERE is_cloud_synced=1").fetchone()["n"]
    conn.close()
    return {
        "count": count,
        "size_bytes": size,
        "size_mb": round(size / 1024 / 1024, 2),
        "oldest_session": oldest,
        "newest_session": newest,
        "cloud_synced": synced
    }
