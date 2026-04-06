from __future__ import annotations


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["indexed_documents"] == 2
    assert data["index_ready"] is True


def test_documents_list(client):
    r = client.get("/api/documents")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    slugs = {x["slug"] for x in items}
    assert slugs == {"hello-world", "second-doc"}
    hw = next(x for x in items if x["slug"] == "hello-world")
    assert "Hello World" in hw["title"]
    assert set(hw["tags"]) == {"alpha", "beta"}
    assert hw["section_count"] >= 2


def test_get_document_markdown(client):
    r = client.get("/api/documents/hello-world")
    assert r.status_code == 200
    d = r.json()
    assert d["slug"] == "hello-world"
    assert "Section A" in d["content_markdown"]
    assert d["content_html"] is None
    anchors = {s["anchor"] for s in d["sections"]}
    assert "section-a" in anchors


def test_get_document_html(client):
    r = client.get("/api/documents/hello-world?format=html")
    assert r.status_code == 200
    d = r.json()
    assert d["content_html"] is not None
    assert "<h1>" in d["content_html"] or "<h1 " in d["content_html"]


def test_section_endpoint(client):
    r = client.get("/api/documents/hello-world/sections/section-a")
    assert r.status_code == 200
    s = r.json()
    assert s["anchor"] == "section-a"
    assert "search" in s["content_markdown"]


def test_search_hits_and_snippet(client):
    r = client.get("/api/search", params={"q": "search"})
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert any("search" in x["snippet"].lower() for x in data["results"])


def test_search_empty_query_400(client):
    r = client.get("/api/search", params={"q": "   "})
    assert r.status_code == 400


def test_search_no_results_200(client):
    r = client.get("/api/search", params={"q": "zzzznonexistenttoken"})
    assert r.status_code == 200
    assert r.json()["results"] == []


def test_search_tag_filter(client):
    r = client.get("/api/search", params={"q": "content", "tag": "alpha"})
    assert r.status_code == 200
    for row in r.json()["results"]:
        assert row["slug"] == "hello-world"


def test_404_document(client):
    r = client.get("/api/documents/missing-slug")
    assert r.status_code == 404


def test_status_alias(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
