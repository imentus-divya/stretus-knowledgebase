from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from kb_server.config import Settings
from kb_server.main import create_app


@pytest.fixture
def content_dir(tmp_path):
    d = tmp_path / "content"
    d.mkdir()
    (d / "hello-world.md").write_text(
        """---
tags: [alpha, beta]
---
# Hello World

First paragraph summary for the document.

## Section A

Some content about **search** and things.

### Nested

Deep content.

## Section B

Other words here.
""",
        encoding="utf-8",
    )
    (d / "second-doc.md").write_text(
        """Tags: gamma, delta

# Second Title

Intro line.

## Part One

Unique token xyz123 for tests.
""",
        encoding="utf-8",
    )
    return d


@pytest.fixture
def settings(content_dir, tmp_path) -> Settings:
    return Settings(
        content_path=content_dir,
        db_path=tmp_path / "kb.db",
        reindex_on_startup=True,
        debug=True,
    )


@pytest.fixture
def client(settings: Settings):
    app = create_app(settings)
    with TestClient(app) as tc:
        yield tc
