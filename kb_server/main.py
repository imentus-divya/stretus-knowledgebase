"""ASGI entrypoint: FastAPI app factory and Uvicorn runner."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from kb_server import __version__
from kb_server.api import register_exception_handlers, router
from kb_server.config import Settings
from kb_server.logging_config import configure_logging, get_logger
from kb_server.repository import KnowledgeRepository

log = get_logger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging(settings.debug)
        content = Path(settings.content_path)
        if not content.is_dir():
            log.warning("content_path_missing", path=str(content.resolve()))
        repo = KnowledgeRepository(settings.db_path)
        repo.open()
        stats = repo.build_index(
            content,
            reindex_on_startup=settings.reindex_on_startup,
        )
        app.state.settings = settings
        app.state.repository = repo
        log.info(
            "startup_complete",
            version=__version__,
            documents=stats.documents_indexed,
            full_rebuild=stats.full_rebuild,
        )
        yield
        repo.close()
        log.info("shutdown_complete")

    app = FastAPI(
        title="Knowledge Base API",
        version=__version__,
        lifespan=lifespan,
        description=(
            "Markdown knowledge base with SQLite FTS5 search. "
            "Search uses FTS5 `MATCH` with token AND-combination; "
            "results are ordered by `bm25()` (lower scores are better matches)."
        ),
    )
    app.include_router(router)
    register_exception_handlers(app)
    return app


def run() -> None:
    settings = Settings()
    configure_logging(settings.debug)
    uvicorn.run(
        "kb_server.main:create_app",
        host=settings.host,
        port=settings.port,
        log_level="debug" if settings.debug else "info",
        factory=True,
    )


if __name__ == "__main__":
    run()
