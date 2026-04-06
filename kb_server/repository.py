"""Persistence, indexing, and FTS search."""

from __future__ import annotations

import re
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kb_server.db import init_schema, recreate_fts_tables, transaction
from kb_server.logging_config import get_logger
from kb_server.markdown_parse import (
    ParsedDocument,
    index_text_for_document,
    load_markdown_file,
    relative_markdown_key,
    scan_markdown_files,
    strip_fenced_code_for_index,
)

log = get_logger(__name__)


def fts5_match_query(q: str) -> str:
    """Build a conservative FTS5 MATCH query (AND of word tokens)."""
    words = re.findall(r"\w+", q, flags=re.UNICODE)
    if not words:
        raise ValueError("empty query")
    return " AND ".join(words)


def section_search_blob(title: str, body: str) -> str:
    return f"{title}\n{strip_fenced_code_for_index(body)}"


@dataclass
class IndexStats:
    documents_indexed: int
    full_rebuild: bool


class KnowledgeRepository:
    """Thread-safe SQLite access for the knowledge base."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        assert self._conn is not None
        return self._conn

    def open(self) -> None:
        from kb_server.db import connect as db_connect

        self._conn = db_connect(self._db_path)
        init_schema(self._conn)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _delete_document_fts(self, conn: sqlite3.Connection, doc_id: int) -> None:
        conn.execute(
            "INSERT INTO documents_fts(documents_fts, rowid) VALUES('delete', ?)",
            (doc_id,),
        )

    def _delete_section_fts(self, conn: sqlite3.Connection, section_id: int) -> None:
        conn.execute(
            "INSERT INTO sections_fts(sections_fts, rowid) VALUES('delete', ?)",
            (section_id,),
        )

    def _remove_document_by_id(self, conn: sqlite3.Connection, doc_id: int) -> None:
        rows = conn.execute(
            "SELECT id FROM sections WHERE document_id=?", (doc_id,)
        ).fetchall()
        for r in rows:
            self._delete_section_fts(conn, r[0])
        self._delete_document_fts(conn, doc_id)
        conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))

    def _insert_document(
        self, conn: sqlite3.Connection, parsed: ParsedDocument
    ) -> int:
        search_text = index_text_for_document(
            parsed.title, parsed.summary, parsed.body_markdown
        )
        conn.execute(
            """
            INSERT INTO documents (slug, title, filename, summary, content, search_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                parsed.slug,
                parsed.title,
                parsed.filename,
                parsed.summary,
                parsed.body_markdown,
                search_text,
            ),
        )
        doc_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            """
            INSERT INTO documents_fts (rowid, title, summary, body)
            VALUES (?, ?, ?, ?)
            """,
            (doc_id, parsed.title, parsed.summary, search_text),
        )
        for tag in parsed.tags:
            conn.execute(
                "INSERT INTO document_tags (document_id, tag) VALUES (?, ?)",
                (doc_id, tag.lower()),
            )
        for sec in parsed.sections:
            sblob = section_search_blob(sec.title, sec.content)
            conn.execute(
                """
                INSERT INTO sections (document_id, anchor, title, level, content, parent_anchor, search_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    sec.anchor,
                    sec.title,
                    sec.level,
                    sec.content,
                    sec.parent_anchor,
                    sblob,
                ),
            )
            sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute(
                """
                INSERT INTO sections_fts (rowid, title, body)
                VALUES (?, ?, ?)
                """,
                (sid, sec.title, sblob),
            )
        return doc_id

    def _fingerprint(self, path: Path) -> tuple[int, int]:
        st = path.stat()
        return (st.st_mtime_ns, st.st_size)

    def _needs_reindex(
        self, conn: sqlite3.Connection, rel: str, path: Path
    ) -> bool:
        mtime_ns, size = self._fingerprint(path)
        row = conn.execute(
            "SELECT mtime_ns, size_bytes FROM file_fingerprints WHERE filename=?",
            (rel,),
        ).fetchone()
        if row is None:
            return True
        return row[0] != mtime_ns or row[1] != size

    def _upsert_fingerprint(
        self, conn: sqlite3.Connection, path: Path, rel: str
    ) -> None:
        mtime_ns, size = self._fingerprint(path)
        conn.execute(
            """
            INSERT INTO file_fingerprints (filename, mtime_ns, size_bytes)
            VALUES (?, ?, ?)
            ON CONFLICT(filename) DO UPDATE SET
              mtime_ns=excluded.mtime_ns,
              size_bytes=excluded.size_bytes
            """,
            (rel, mtime_ns, size),
        )

    def build_index(
        self,
        content_dir: Path,
        *,
        reindex_on_startup: bool,
    ) -> IndexStats:
        with self._lock:
            conn = self.conn
            files = scan_markdown_files(content_dir, recursive=True)
            if reindex_on_startup:
                with transaction(conn):
                    conn.execute("DELETE FROM sections_fts")
                    conn.execute("DELETE FROM documents_fts")
                    conn.execute("DELETE FROM sections")
                    conn.execute("DELETE FROM document_tags")
                    conn.execute("DELETE FROM documents")
                    conn.execute("DELETE FROM file_fingerprints")
                    recreate_fts_tables(conn)
                    n = 0
                    for path in files:
                        parsed = load_markdown_file(path, content_root=content_dir)
                        if not parsed:
                            continue
                        self._insert_document(conn, parsed)
                        rel = relative_markdown_key(path, content_dir)
                        self._upsert_fingerprint(conn, path, rel)
                        n += 1
                log.info("index_full_rebuild", documents=n)
                return IndexStats(documents_indexed=n, full_rebuild=True)

            # incremental
            on_disk = {
                relative_markdown_key(p, content_dir): p for p in files
            }
            rows = conn.execute("SELECT filename FROM documents").fetchall()
            known_filenames = {r[0] for r in rows}

            to_refresh: list[Path] = []
            for rel, path in on_disk.items():
                if self._needs_reindex(conn, rel, path):
                    to_refresh.append(path)

            for fn in known_filenames:
                if fn not in on_disk:
                    row = conn.execute(
                        "SELECT id FROM documents WHERE filename=?", (fn,)
                    ).fetchone()
                    if row:
                        with transaction(conn):
                            self._remove_document_by_id(conn, row[0])
                            conn.execute(
                                "DELETE FROM file_fingerprints WHERE filename=?",
                                (fn,),
                            )

            n_changed = 0
            for path in to_refresh:
                parsed = load_markdown_file(path, content_root=content_dir)
                if not parsed:
                    continue
                rel = relative_markdown_key(path, content_dir)
                with transaction(conn):
                    row = conn.execute(
                        "SELECT id FROM documents WHERE filename=?", (rel,)
                    ).fetchone()
                    if row:
                        self._remove_document_by_id(conn, row[0])
                    self._insert_document(conn, parsed)
                    self._upsert_fingerprint(conn, path, rel)
                    n_changed += 1

            total = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            log.info(
                "index_incremental",
                refreshed=n_changed,
                total_documents=total,
            )
            return IndexStats(documents_indexed=total, full_rebuild=False)

    def count_documents(self) -> int:
        with self._lock:
            r = self.conn.execute("SELECT COUNT(*) FROM documents").fetchone()
            return int(r[0]) if r else 0

    def list_documents(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT d.slug, d.title, d.summary,
                  (SELECT COUNT(*) FROM sections s WHERE s.document_id = d.id) AS sc,
                  GROUP_CONCAT(dt.tag, ',') AS tags
                FROM documents d
                LEFT JOIN document_tags dt ON dt.document_id = d.id
                GROUP BY d.id
                ORDER BY d.slug
                """
            ).fetchall()
        out: list[dict[str, Any]] = []
        for r in rows:
            tags = [t for t in (r[4] or "").split(",") if t]
            out.append(
                {
                    "slug": r[0],
                    "title": r[1],
                    "summary": r[2],
                    "section_count": int(r[3]),
                    "tags": tags,
                }
            )
        return out

    def get_document(self, slug: str) -> dict[str, Any] | None:
        with self._lock:
            row = self.conn.execute(
                "SELECT id, slug, title, summary, content FROM documents WHERE slug=?",
                (slug,),
            ).fetchone()
            if not row:
                return None
            doc_id = row[0]
            tags = [
                r[0]
                for r in self.conn.execute(
                    "SELECT tag FROM document_tags WHERE document_id=? ORDER BY tag",
                    (doc_id,),
                ).fetchall()
            ]
            secs = self.conn.execute(
                "SELECT anchor, title, level FROM sections WHERE document_id=? ORDER BY id",
                (doc_id,),
            ).fetchall()
            return {
                "slug": row[1],
                "title": row[2],
                "summary": row[3],
                "content_markdown": row[4],
                "tags": tags,
                "sections": [
                    {"anchor": s[0], "title": s[1], "level": s[2]} for s in secs
                ],
            }

    def get_section(self, slug: str, anchor: str) -> dict[str, Any] | None:
        with self._lock:
            row = self.conn.execute(
                """
                SELECT s.anchor, s.title, s.level, s.content
                FROM sections s
                JOIN documents d ON d.id = s.document_id
                WHERE d.slug=? AND s.anchor=?
                """,
                (slug, anchor),
            ).fetchone()
            if not row:
                return None
            return {
                "anchor": row[0],
                "title": row[1],
                "level": row[2],
                "content_markdown": row[3],
            }

    def list_section_meta(self, slug: str) -> list[dict[str, Any]] | None:
        with self._lock:
            doc = self.conn.execute(
                "SELECT id FROM documents WHERE slug=?", (slug,)
            ).fetchone()
            if not doc:
                return None
            rows = self.conn.execute(
                """
                SELECT anchor, title, level, parent_anchor
                FROM sections WHERE document_id=? ORDER BY id
                """,
                (doc[0],),
            ).fetchall()
            return [
                {
                    "anchor": r[0],
                    "title": r[1],
                    "level": r[2],
                    "parent_anchor": r[3],
                }
                for r in rows
            ]

    def search(
        self,
        q: str,
        *,
        limit: int,
        snippet_len: int,
        tag: str | None,
    ) -> list[dict[str, Any]]:
        mq = fts5_match_query(q)
        params_doc: list[Any] = [mq]
        params_sec: list[Any] = [mq]
        tag_sql_doc = ""
        tag_sql_sec = ""
        if tag:
            tag_sql_doc = """
              AND EXISTS (
                SELECT 1 FROM document_tags dt
                WHERE dt.document_id = d.id AND dt.tag = ?
              )
            """
            tag_sql_sec = """
              AND EXISTS (
                SELECT 1 FROM document_tags dt
                WHERE dt.document_id = d.id AND dt.tag = ?
              )
            """
            params_doc.append(tag.lower())
            params_sec.append(tag.lower())

        with self._lock:
            conn = self.conn
            tok = max(8, min(snippet_len // 4, 64))
            doc_sql = f"""
              SELECT 'doc' AS src, d.slug, d.title,
                snippet(documents_fts, 2, '<b>', '</b>', ' … ', {tok}) AS snip,
                CAST(bm25(documents_fts) AS REAL) AS score,
                NULL AS anchor
              FROM documents_fts
              JOIN documents d ON d.id = documents_fts.rowid
              WHERE documents_fts MATCH ?
              {tag_sql_doc}
            """
            sec_sql = f"""
              SELECT 'sec' AS src, d.slug, d.title,
                snippet(sections_fts, 1, '<b>', '</b>', ' … ', {tok}) AS snip,
                CAST(bm25(sections_fts) AS REAL) AS score,
                s.anchor AS anchor
              FROM sections_fts
              JOIN sections s ON s.id = sections_fts.rowid
              JOIN documents d ON d.id = s.document_id
              WHERE sections_fts MATCH ?
              {tag_sql_sec}
            """
            rows = conn.execute(
                f"""
                SELECT * FROM (
                  {doc_sql}
                  UNION ALL
                  {sec_sql}
                )
                ORDER BY score ASC
                LIMIT ?
                """,
                (*params_doc, *params_sec, limit * 4),
            ).fetchall()

        best: dict[tuple[str, str | None], dict[str, Any]] = {}
        order_keys: list[tuple[str, str | None]] = []
        for r in rows:
            _src, slug, title, snip, score, anchor = r
            key = (slug, anchor)
            if key not in best:
                order_keys.append(key)
            prev = best.get(key)
            if prev is None or float(score) < prev["score"]:
                matched_tags: list[str] = [tag] if tag else []
                best[key] = {
                    "slug": slug,
                    "title": title,
                    "snippet": snip[:snippet_len] if len(snip) > snippet_len else snip,
                    "anchor": anchor,
                    "score": float(score),
                    "matched_tags": matched_tags,
                }
        merged = [best[k] for k in order_keys if k in best]
        merged.sort(key=lambda x: x["score"])
        slugs_with_section = {m["slug"] for m in merged if m.get("anchor")}
        merged = [
            m
            for m in merged
            if not (m["slug"] in slugs_with_section and m.get("anchor") is None)
        ]
        return merged[:limit]
