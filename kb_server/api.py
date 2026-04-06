"""HTTP routes for the knowledge base API."""

from __future__ import annotations

import traceback

import markdown
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from kb_server.logging_config import get_logger
from kb_server.models import (
    DocumentDetail,
    DocumentListItem,
    HealthResponse,
    SearchResponse,
    SearchResultItem,
    SectionDetail,
    SectionMeta,
)

log = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

_MD_EXTENSIONS = ["extra", "sane_lists", "smarty"]


def _repo(request: Request):
    return request.app.state.repository


def _settings(request: Request):
    return request.app.state.settings


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    repo = _repo(request)
    settings = _settings(request)
    n = repo.count_documents()
    return HealthResponse(
        status="ok",
        indexed_documents=n,
        index_ready=n >= 0,
        db_path=str(settings.db_path.resolve()),
        content_path=str(settings.content_path.resolve()),
    )


@router.get("/status", response_model=HealthResponse)
def status(request: Request) -> HealthResponse:
    return health(request)


@router.get("/documents", response_model=list[DocumentListItem])
def list_documents(request: Request) -> list[DocumentListItem]:
    rows = _repo(request).list_documents()
    return [DocumentListItem(**r) for r in rows]


@router.get("/documents/{slug}", response_model=DocumentDetail)
def get_document(
    request: Request,
    slug: str,
    format: str | None = Query(default=None, description="Use `html` for rendered body"),
) -> DocumentDetail:
    repo = _repo(request)
    row = repo.get_document(slug)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    data = dict(row)
    if format == "html":
        data["content_html"] = markdown.markdown(
            data["content_markdown"],
            extensions=_MD_EXTENSIONS,
        )
    else:
        data["content_html"] = None
    return DocumentDetail(**data)


@router.get("/documents/{slug}/sections", response_model=list[SectionMeta])
def list_sections(request: Request, slug: str) -> list[SectionMeta]:
    repo = _repo(request)
    meta = repo.list_section_meta(slug)
    if meta is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return [
        SectionMeta(anchor=m["anchor"], title=m["title"], level=m["level"]) for m in meta
    ]


@router.get(
    "/documents/{slug}/sections/{anchor}",
    response_model=SectionDetail,
)
def get_section(request: Request, slug: str, anchor: str) -> SectionDetail:
    repo = _repo(request)
    row = repo.get_section(slug, anchor)
    if not row:
        raise HTTPException(status_code=404, detail="Section not found")
    return SectionDetail(**row)


@router.get("/search", response_model=SearchResponse)
def search(
    request: Request,
    q: str = Query(..., description="Search query (FTS5 MATCH; words are AND-combined)"),
    limit: int | None = None,
    tag: str | None = None,
) -> SearchResponse:
    settings = _settings(request)
    lim = limit if limit is not None else settings.default_search_limit
    lim = max(1, min(lim, settings.max_search_limit))
    q = q.strip()
    if not q:
        raise HTTPException(
            status_code=400,
            detail="Query must not be empty",
        )
    repo = _repo(request)
    try:
        rows = repo.search(
            q,
            limit=lim,
            snippet_len=settings.snippet_length,
            tag=tag,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    results = [
        SearchResultItem(
            slug=r["slug"],
            title=r["title"],
            snippet=r["snippet"],
            anchor=r["anchor"],
            score=r["score"],
            matched_tags=r.get("matched_tags", []),
        )
        for r in rows
    ]
    return SearchResponse(results=results, query=q)


def register_exception_handlers(app) -> None:
    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        log.error(
            "unhandled_error",
            path=str(request.url.path),
            error=str(exc),
            traceback=traceback.format_exc(),
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
