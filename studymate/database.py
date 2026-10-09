import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "studymate.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection and ensure the history table exists."""
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            session_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()

    return connection


def save_session(
    title: str,
    session_type: str,
    content: dict[str, Any],
) -> int:
    """Save a generated result and return its database ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO study_sessions (title, session_type, content)
            VALUES (?, ?, ?)
            """,
            (
                title.strip()[:200] or "Untitled session",
                session_type,
                json.dumps(content, ensure_ascii=False),
            ),
        )
        return int(cursor.lastrowid)


def list_sessions(limit: int = 50) -> list[dict[str, Any]]:
    """Return the newest saved sessions first."""
    limit = max(1, min(int(limit), 200))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, session_type, created_at
            FROM study_sessions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_session(session_id: int) -> dict[str, Any] | None:
    """Load one saved session by its ID."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, session_type, content, created_at
            FROM study_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

    if row is None:
        return None

    result = dict(row)
    result["content"] = json.loads(result["content"])
    return result


def delete_session(session_id: int) -> bool:
    """Delete a saved session. Return True if a row was removed."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM study_sessions WHERE id = ?",
            (session_id,),
        )
        return cursor.rowcount > 0
