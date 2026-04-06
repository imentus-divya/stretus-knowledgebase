"""Markdown document loading, section splitting, and search-index text preparation."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from kb_server.logging_config import get_logger

log = get_logger(__name__)

FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TAGS_LINE = re.compile(r"^Tags?:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE)
HEADING_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
FENCED_CODE = re.compile(r"```[\s\S]*?```", re.MULTILINE)


def slug_from_filename(filename: str) -> str:
    """Lowercase, URL-safe slug from basename without extension."""
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9\-_.]+", "-", stem, flags=re.IGNORECASE)
    stem = re.sub(r"-+", "-", stem).strip("-._")
    return stem or "document"


def slug_from_relative_path(rel: str) -> str:
    """URL-safe slug from a path relative to the content root (e.g. folder/file.md)."""
    s = rel.replace("\\", "/")
    if s.lower().endswith(".md"):
        s = s[:-3]
    s = s.replace("/", "-").lower()
    s = re.sub(r"[^a-z0-9\-_.]+", "-", s, flags=re.IGNORECASE)
    s = re.sub(r"-+", "-", s).strip("-._")
    return s or "document"


def relative_markdown_key(path: Path, content_root: Path) -> str:
    """Stable posix key for DB/fingerprints (e.g. 10-trading-signals/ema-crossover.md)."""
    return path.resolve().relative_to(content_root.resolve()).as_posix()


def _normalize_anchor_base(text: str) -> str:
    s = unicodedata.normalize("NFKD", text.strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s\-]+", "", s)
    s = re.sub(r"[\s\-]+", "-", s).strip("-")
    return s or "section"


def make_unique_anchor(base: str, seen: dict[str, int]) -> str:
    n = seen.get(base, 0)
    seen[base] = n + 1
    if n == 0:
        return base
    return f"{base}-{n + 1}"


def strip_fenced_code_for_index(md: str) -> str:
    """Replace fenced code blocks with spaces so FTS does not match inside code."""
    return FENCED_CODE.sub(" ", md)


def strip_inline_markdown_for_summary(text: str) -> str:
    """Light cleanup for summary / snippet display."""
    t = re.sub(r"`+([^`]+)`+", r"\1", text)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[*_#]+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_first_paragraph_after_title(body: str) -> str:
    """First non-empty paragraph after optional title line (H1 handled separately)."""
    lines = body.splitlines()
    i = 0
    if lines and lines[0].strip().startswith("#"):
        i = 1
    buf: list[str] = []
    for j in range(i, len(lines)):
        line = lines[j].strip()
        if not line:
            if buf:
                break
            continue
        if line.startswith("#"):
            break
        buf.append(line)
    return " ".join(buf)


@dataclass
class ParsedSection:
    level: int
    title: str
    anchor: str
    parent_anchor: str | None
    content: str


@dataclass
class ParsedDocument:
    slug: str
    filename: str
    title: str
    summary: str
    tags: list[str]
    body_markdown: str
    sections: list[ParsedSection] = field(default_factory=list)


def _parse_front_matter(raw: str) -> tuple[dict, str]:
    m = FRONT_MATTER.match(raw)
    if not m:
        return {}, raw
    try:
        meta = yaml.safe_load(m.group(1)) or {}
        if not isinstance(meta, dict):
            meta = {}
    except yaml.YAMLError as e:
        log.warning("front_matter_parse_failed", error=str(e))
        meta = {}
    rest = raw[m.end() :]
    return meta, rest


def _tags_from_meta_and_body(meta: dict, body: str) -> list[str]:
    tags: list[str] = []
    if isinstance(meta.get("tags"), list):
        tags = [str(t).strip() for t in meta["tags"] if str(t).strip()]
    elif isinstance(meta.get("tags"), str):
        tags = [t.strip() for t in meta["tags"].split(",") if t.strip()]
    if not tags:
        tm = TAGS_LINE.search(body)
        if tm:
            tags = [t.strip() for t in tm.group(1).split(",") if t.strip()]
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def _first_h1_title(body: str) -> str | None:
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return m.group(1).strip() if m else None


def _split_sections(body: str) -> list[ParsedSection]:
    """Split by headings; section content runs until next heading of same or higher level (lower or equal # count)."""
    matches = list(HEADING_LINE.finditer(body))
    if not matches:
        return []

    sections: list[ParsedSection] = []
    anchor_seen: dict[str, int] = {}
    stack: list[tuple[int, str]] = []

    for i, m in enumerate(matches):
        hashes = m.group(1)
        level = len(hashes)
        title = m.group(2).strip()
        heading_end = m.end()
        start_content = heading_end
        end_content = len(body)
        for j in range(i + 1, len(matches)):
            next_level = len(matches[j].group(1))
            if next_level <= level:
                end_content = matches[j].start()
                break

        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_anchor = stack[-1][1] if stack else None
        base = _normalize_anchor_base(title)
        anchor = make_unique_anchor(base, anchor_seen)
        stack.append((level, anchor))
        content = body[start_content:end_content].strip()
        sections.append(
            ParsedSection(
                level=level,
                title=title,
                anchor=anchor,
                parent_anchor=parent_anchor,
                content=content,
            )
        )
    return sections


def _build_summary(body: str, title_fallback: str) -> str:
    h1 = _first_h1_title(body)
    if h1:
        rest = body
        m = re.search(r"^#\s+.+\n", body, re.MULTILINE)
        if m:
            rest = body[m.end() :]
    else:
        rest = body
    para = extract_first_paragraph_after_title(rest if h1 else body)
    if not para:
        para = strip_inline_markdown_for_summary(body)[:220]
    else:
        para = strip_inline_markdown_for_summary(para)
    if len(para) > 220:
        para = para[:217].rstrip() + "..."
    return para or title_fallback


def load_markdown_file(
    path: Path, *, content_root: Path | None = None
) -> ParsedDocument | None:
    """Load and parse one UTF-8 markdown file. Returns None on unreadable content.

    When ``content_root`` is set, ``filename`` and ``slug`` reflect the path under
    that root so nested folders (e.g. ``10-trading-signals/foo.md``) stay unique.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        log.error("file_not_utf8_skipped", path=str(path), error=str(e))
        return None
    except OSError as e:
        log.error("file_read_error", path=str(path), error=str(e))
        return None

    meta, body = _parse_front_matter(raw)
    if not meta and raw.startswith("---"):
        body = raw

    tags = _tags_from_meta_and_body(meta, body)
    if content_root is not None:
        filename = relative_markdown_key(path, content_root)
        slug = slug_from_relative_path(filename)
    else:
        filename = path.name
        slug = slug_from_filename(filename)
    h1 = _first_h1_title(body)
    title = h1 if h1 else Path(filename).stem.replace("-", " ").replace("_", " ").title()
    summary = _build_summary(body, title)
    sections = _split_sections(body)
    return ParsedDocument(
        slug=slug,
        filename=filename,
        title=title,
        summary=summary,
        tags=tags,
        body_markdown=body,
        sections=sections,
    )


def scan_markdown_files(content_dir: Path, *, recursive: bool = True) -> list[Path]:
    """Discover ``*.md`` files. Default: recursive (subfolders included)."""
    if not content_dir.is_dir():
        return []
    if recursive:
        return sorted(content_dir.rglob("*.md"))
    return sorted(content_dir.glob("*.md"))


def index_text_for_document(title: str, summary: str, body: str) -> str:
    """Plain text blob for FTS documents table (code stripped)."""
    stripped = strip_fenced_code_for_index(body)
    return f"{title}\n{summary}\n{stripped}"
