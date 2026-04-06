# Stretus Knowledge Base

A standalone **Python** service that indexes **Markdown** documentation from disk and serves it through a **JSON REST API** with **full-text search** (SQLite **FTS5**). Content lives as normal `.md` files; the database is a local SQLite file used for fast queries and search ranking.

**Stack:** FastAPI, Uvicorn, Pydantic v2, structlog, PyYAML, optional HTML rendering via the `markdown` package.

---

## Table of contents

1. [Features](#features)  
2. [How it works](#how-it-works)  
3. [Requirements](#requirements)  
4. [Installation](#installation)  
5. [Running the server](#running-the-server)  
6. [Configuration](#configuration)  
7. [Content layout and slugs](#content-layout-and-slugs)  
8. [Indexing behaviour](#indexing-behaviour)  
9. [REST API](#rest-api)  
10. [Search](#search)  
11. [Docker](#docker)  
12. [Development and tests](#development-and-tests)  
13. [Project structure](#project-structure)  
14. [Security and production](#security-and-production)  
15. [Troubleshooting](#troubleshooting)  

---

## Features

- Serves Markdown from a configurable directory (`KB_CONTENT_PATH`).
- **Recursive** discovery of all `*.md` files under that directory (subfolders supported).
- Parses titles, summaries, optional YAML/`Tags:` lines, and heading-based **sections** with stable anchors.
- **SQLite** storage plus **FTS5** indexes for documents and sections; **BM25** ranking and highlighted snippets.
- Health and status endpoints for operators.
- Optional **HTML** body for a document via `?format=html`.
- **Docker Compose** with mounted content and a persistent database volume.
- **pytest** suite (no network required).

---

## How it works

1. **Startup:** The app opens (or creates) a SQLite database at `KB_DB_PATH`, ensures schema and FTS virtual tables, then **indexes** Markdown from `KB_CONTENT_PATH` according to `KB_REINDEX_ON_STARTUP`.
2. **Storage:** Each file becomes a **document** row; headings become **section** rows; tags are stored separately. Searchable text for FTS **strips fenced code blocks** so matches and snippets stay meaningful.
3. **Runtime:** HTTP handlers read from SQLite (and FTS for search). **No** hot-reload of files: after you edit Markdown, restart the process (or rely on incremental indexing on the next start if configured).

---

## Requirements

- **Python 3.11+**
- SQLite with **FTS5** (bundled with Python on most platforms)

---

## Installation

Clone the repository and install in a virtual environment.

```bash
cd stretus-knowledgebase
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e .
```

For local development (tests, linting tools you add yourself):

```bash
pip install -e ".[dev]"
```

Optional: create a `.env` file in the project root; variables are documented in [Configuration](#configuration). Pydantic loads `.env` automatically when present.

---

## Running the server

Set paths if you do not use defaults (`./content`, `./data/kb.db`).

### Option 1: Uvicorn (recommended)

The application is exposed as a **factory** (`create_app`) so settings are loaded per process:

```bash
export KB_CONTENT_PATH=./content
export KB_DB_PATH=./data/kb.db

python -m uvicorn kb_server.main:create_app --factory --host 0.0.0.0 --port 8080
```

### Option 2: Console script

After `pip install -e .`, the `kb-server` entry point runs Uvicorn with the same factory:

```bash
kb-server
```

Environment variables (e.g. `KB_PORT`) apply the same way.

### Verify

- Open: `http://127.0.0.1:8080/api/health`  
- List documents: `http://127.0.0.1:8080/api/documents`  
- Interactive docs: `http://127.0.0.1:8080/docs` (FastAPI Swagger UI)

---

## Configuration

All environment variables use the prefix **`KB_`**. Names map to the `Settings` class in `kb_server/config.py` (e.g. `KB_CONTENT_PATH` → `content_path`).

| Variable | Default | Description |
|----------|---------|-------------|
| `KB_HOST` | `0.0.0.0` | Address the server binds to. |
| `KB_PORT` | `8080` | TCP port. |
| `KB_CONTENT_PATH` | `./content` | Root directory scanned for `*.md` files (recursive). |
| `KB_DB_PATH` | `./data/kb.db` | SQLite database file path (parent directories are created if needed). |
| `KB_DEBUG` | `false` | If `true`, more verbose logging; console-friendly log rendering in development. |
| `KB_SNIPPET_LENGTH` | `240` | Upper bound on snippet length after FTS `snippet()` (characters). |
| `KB_DEFAULT_SEARCH_LIMIT` | `20` | Default `limit` for `/api/search` when omitted. |
| `KB_MAX_SEARCH_LIMIT` | `100` | Maximum allowed `limit` for `/api/search`. |
| `KB_REINDEX_ON_STARTUP` | `true` | If `true`, full reindex on every startup; if `false`, [incremental](#indexing-behaviour) indexing. |

Example:

```bash
export KB_CONTENT_PATH=/var/kb/content
export KB_DB_PATH=/var/kb/data/kb.db
export KB_REINDEX_ON_STARTUP=false
```

---

## Content layout and slugs

- **Scan:** Every `*.md` file under `KB_CONTENT_PATH` is included, **including nested directories** (e.g. `content/10-trading-signals/ema-crossover.md`).
- **Slug (API identifier):**
  - For a file at the root of the content path, the slug is derived from the **filename** (without extension), lowercased and URL-safe.
  - For a file in a subfolder, the slug is derived from the **full relative path**: path separators become hyphens.  
    Example: `10-trading-signals/ema-crossover.md` → slug **`10-trading-signals-ema-crossover`**.  
    Use this value in URLs such as `/api/documents/{slug}`.
- **Title:** First Markdown `#` (H1) line in the file; if missing, a humanized title from the filename stem.
- **Summary:** First paragraph after the title block, or a short cleaned excerpt of the body.
- **Tags:** Optional. **Precedence:** (1) YAML front matter `tags:` list or string; (2) if still empty, a body line matching `Tags:` or `Tag:` with comma-separated values.
- **Sections:** Headings `#` … `######` split the document. Section body runs until the next heading of the **same or higher** level (standard outline behaviour). Each section gets an **anchor** (Unicode-normalized, lowercased, hyphenated; duplicates get numeric suffixes within the file).
- **Encoding:** Files must be **UTF-8**. Invalid files are logged and skipped; the rest of the index still loads.
- **Code in search:** Fenced `` ``` `` blocks are replaced with spaces in the indexed search text so FTS does not match inside code blocks.

---

## Indexing behaviour

| `KB_REINDEX_ON_STARTUP` | Behaviour |
|-------------------------|-----------|
| **`true`** (default) | On startup: existing documents, sections, tags, fingerprints, and FTS data are cleared; FTS tables are recreated; all Markdown files are re-ingested inside a transaction. |
| **`false`** | **Incremental:** For each file, last known `mtime` and size are stored in `file_fingerprints`. Only new, changed, or removed files are processed; unchanged files are skipped. |

After editing files on disk, **restart the server** so indexing runs again (full or incremental per setting).

---

## REST API

Base path: **`/api`**. Responses are JSON unless noted. Errors use FastAPI’s shape: `{ "detail": ... }`.

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Liveness: `status`, `indexed_documents`, `index_ready`, `db_path`, `content_path`. |
| GET | `/api/status` | Same payload as `/api/health`. |

### Documents

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/documents` | List all documents: `slug`, `title`, `summary`, `tags`, `section_count`. |
| GET | `/api/documents/{slug}` | Full document: `content_markdown`, `sections` (metadata), `tags`, etc. Query: `format=html` adds rendered `content_html` (Markdown → HTML). |
| GET | `/api/documents/{slug}/sections` | Section list: `anchor`, `title`, `level` (no full body). |
| GET | `/api/documents/{slug}/sections/{anchor}` | One section: `content_markdown` and metadata. |

Unknown `slug` or `anchor` → **404**.

---

## Search

| Method | Path | Query parameters |
|--------|------|-------------------|
| GET | `/api/search` | **`q`** (required, non-empty after trim), **`limit`** (optional, capped by `KB_MAX_SEARCH_LIMIT`), **`tag`** (optional; restrict to documents that have this tag). |

Response shape:

```json
{
  "query": "string",
  "results": [
    {
      "slug": "string",
      "title": "string",
      "snippet": "string",
      "anchor": "string or null",
      "score": 0.0,
      "matched_tags": []
    }
  ]
}
```

- **Ranking:** FTS5 **`bm25()`** on the virtual tables; **lower score = better match** in the usual BM25 interpretation used here.
- **Snippets:** FTS5 **`snippet()`** with `<b>`…`</b>` markers around matches; length is influenced by `KB_SNIPPET_LENGTH`.
- **Query parsing:** Alphanumeric tokens are combined with **`AND`** for the FTS `MATCH` expression.
- **Empty query:** **400 Bad Request.**
- **No matches:** **200** with an empty `results` array.
- **Section vs document:** If both a document-level and section-level hit exist for the same document, section-level hits are preferred so anchors can be shown when relevant.

---

## Docker

Build and run with Compose from the repository root:

```bash
docker compose up --build
```

- **Content:** `./content` on the host is mounted read-only at `/kb/content` inside the container.
- **Database:** Named volume `kb_data` persists `/kb/data/kb.db` so the search index survives container restarts.
- **Environment:** See `docker-compose.yml` for defaults (`KB_REINDEX_ON_STARTUP` is `false` in the sample compose file so routine restarts avoid a full rebuild; adjust if you prefer a full reindex every start).

To rebuild the image after code changes:

```bash
docker compose build --no-cache
```

---

## Development and tests

```bash
pip install -e ".[dev]"
pytest
```

Tests use Starlette’s `TestClient` (lifespan runs) and include an optional **httpx** `AsyncClient` example with **asgi-lifespan** for async smoke tests. No network access is required for the suite.

---

## Project structure

```
stretus-knowledgebase/
├── content/                 # Your Markdown tree (example + your docs)
├── kb_server/
│   ├── main.py              # App factory, lifespan, Uvicorn entry
│   ├── config.py            # Environment-based Settings
│   ├── api.py               # REST routes
│   ├── models.py            # Pydantic response models
│   ├── db.py                # SQLite schema and FTS setup
│   ├── repository.py        # Indexing, queries, search
│   ├── markdown_parse.py    # Parsing, slugs, sections, search text
│   └── logging_config.py    # structlog configuration
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Security and production

- This service does **not** ship authentication. Do not expose it directly on the public internet; put it behind a reverse proxy (nginx, Caddy, Traefik, cloud LB) with **TLS**, access control, and rate limiting as needed.
- `/api/health` returns resolved filesystem paths; restrict access if paths are sensitive.
- Back up **`KB_DB_PATH`** and your **`KB_CONTENT_PATH`** tree; the DB can always be rebuilt from Markdown with a full reindex.
- For multi-worker deployments, SQLite is typically **one writer**; prefer a single process or a single indexing worker, or move to a client/server database if you outgrow file locking.

---

## Troubleshooting

| Issue | What to check |
|--------|----------------|
| Empty document list | `KB_CONTENT_PATH` exists and contains `*.md` files; check logs for skipped files (encoding errors). |
| Old content in API | Restart the server after edits; ensure indexing ran (see `/api/health` `indexed_documents`). |
| Search returns nothing | Try simpler `q` tokens; confirm files were indexed; remember code blocks are not searchable. |
| Port in use | Change `KB_PORT` or stop the other process using the port. |
| Docker shows no new docs | Volume mount path, file permissions, and `KB_REINDEX_ON_STARTUP` / restart after adding files. |

---

## License

Add a `LICENSE` file in the repository if you distribute this project; the package metadata in `pyproject.toml` does not set a license field by default.
