from __future__ import annotations

from pathlib import Path

from kb_server.markdown_parse import (
    load_markdown_file,
    slug_from_filename,
    slug_from_relative_path,
)


def test_slug_from_filename():
    assert slug_from_filename("01-indian-market-foundations.md") == "01-indian-market-foundations"
    assert slug_from_filename("My File Name.MD") == "my-file-name"


def test_slug_from_relative_path_nested():
    assert (
        slug_from_relative_path("10-trading-signals/ema-crossover.md")
        == "10-trading-signals-ema-crossover"
    )


def test_tags_precedence_yaml_over_line(tmp_path: Path):
    p = tmp_path / "t.md"
    p.write_text(
        """---
tags: [from-yaml]
---
Tags: from-line

# T

Body.
""",
        encoding="utf-8",
    )
    doc = load_markdown_file(p)
    assert doc is not None
    assert doc.tags == ["from-yaml"]


def test_tags_line_when_no_yaml(tmp_path: Path):
    p = tmp_path / "t.md"
    p.write_text(
        """Tags: one, two

# Hello

Text.
""",
        encoding="utf-8",
    )
    doc = load_markdown_file(p)
    assert doc is not None
    assert set(doc.tags) == {"one", "two"}
