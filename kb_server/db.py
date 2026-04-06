"""SQLite schema, FTS5 setup (Porter when available), and connection helpers."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from kb_server.logging_config import get_logger

log = get_logger(__name__)

SCHEMA_VERSION = 1


def _detect_fts_tokenizer(conn: sqlite3.Connection) -> str:
    """Prefer Porter stemming; fall back to unicode61."""
    for spec in ("porter", "unicode61"):
        try:
            conn.execute(
                f"CREATE VIRTUAL TABLE _fts_probe USING fts5(x, tokenize='{spec}');"
            )
            conn.execute("DROP TABLE _fts_probe;")
            log.info("fts_tokenizer_selected", tokenizer=spec)
            return spec
        except sqlite3.OperationalError:
            continue
    log.warning("fts_tokenizer_fallback", tokenizer="default")
    return ""


def _fts_tables_exist(conn: sqlite3.Connection) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='documents_fts' LIMIT 1"
    )
    return cur.fetchone() is not None


def init_schema(conn: sqlite3.Connection) -> None:
    tok = _detect_fts_tokenizer(conn)
    tokenize_clause = f", tokenize='{tok}'" if tok else ""

    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS schema_meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS file_fingerprints (
          filename TEXT PRIMARY KEY,
          mtime_ns INTEGER NOT NULL,
          size_bytes INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          slug TEXT NOT NULL UNIQUE,
          title TEXT NOT NULL,
          filename TEXT NOT NULL,
          summary TEXT NOT NULL DEFAULT '',
          content TEXT NOT NULL,
          search_text TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS document_tags (
          document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
          tag TEXT NOT NULL,
          PRIMARY KEY (document_id, tag)
        );

        CREATE TABLE IF NOT EXISTS sections (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
          anchor TEXT NOT NULL,
          title TEXT NOT NULL,
          level INTEGER NOT NULL,
          content TEXT NOT NULL,
          parent_anchor TEXT,
          search_text TEXT NOT NULL,
          UNIQUE(document_id, anchor)
        );

        CREATE INDEX IF NOT EXISTS idx_sections_doc ON sections(document_id);
        CREATE INDEX IF NOT EXISTS idx_tags_tag ON document_tags(tag);
        """
    )

    if _fts_tables_exist(conn):
        conn.commit()
        return

    conn.execute(
        f"""
        CREATE VIRTUAL TABLE documents_fts USING fts5(
          title,
          summary,
          body
          {tokenize_clause}
        );
        """
    )
    conn.execute(
        f"""
        CREATE VIRTUAL TABLE sections_fts USING fts5(
          title,
          body
          {tokenize_clause}
        );
        """
    )
    conn.execute(
        "INSERT OR REPLACE INTO schema_meta(key, value) VALUES ('version', ?)",
        (str(SCHEMA_VERSION),),
    )
    conn.commit()


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Generator[None, None, None]:
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def drop_fts_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS documents_fts")
    conn.execute("DROP TABLE IF EXISTS sections_fts")


def recreate_fts_tables(conn: sqlite3.Connection) -> None:
    """Recreate empty FTS5 virtual tables (same tokenizer as init)."""
    tok = _detect_fts_tokenizer(conn)
    tokenize_clause = f", tokenize='{tok}'" if tok else ""
    drop_fts_tables(conn)
    conn.execute(
        f"""
        CREATE VIRTUAL TABLE documents_fts USING fts5(
          title,
          summary,
          body
          {tokenize_clause}
        );
        """
    )
    conn.execute(
        f"""
        CREATE VIRTUAL TABLE sections_fts USING fts5(
          title,
          body
          {tokenize_clause}
        );
        """
    )
