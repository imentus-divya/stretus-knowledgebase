from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    indexed_documents: int
    index_ready: bool
    db_path: str
    content_path: str


class DocumentListItem(BaseModel):
    slug: str
    title: str
    summary: str
    tags: list[str]
    section_count: int


class SectionMeta(BaseModel):
    anchor: str
    title: str
    level: int


class DocumentDetail(BaseModel):
    slug: str
    title: str
    summary: str
    tags: list[str]
    content_markdown: str
    content_html: str | None = None
    sections: list[SectionMeta]


class SectionDetail(BaseModel):
    anchor: str
    title: str
    level: int
    content_markdown: str


class SearchResultItem(BaseModel):
    slug: str
    title: str
    snippet: str
    anchor: str | None = None
    score: float
    matched_tags: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    query: str


class ErrorDetail(BaseModel):
    detail: str
