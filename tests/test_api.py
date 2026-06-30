from pathlib import Path

from fastapi.testclient import TestClient

from search_engine.api.app import create_app
from search_engine.index import IndexStore
from search_engine.mapreduce import build_index


def test_api_endpoints(tmp_path, monkeypatch):
    index_dir = tmp_path / "index"
    IndexStore(index_dir).save(build_index(Path("data/sample_corpus"), shards=4))
    monkeypatch.setenv("SEARCH_INDEX_DIR", str(index_dir))

    client = TestClient(create_app())

    assert client.get("/health").json() == {"status": "ok"}
    stats = client.get("/stats").json()
    assert stats["document_count"] == 6

    search = client.get("/search", params={"q": "page rank", "k": 2}).json()
    assert search["count"] >= 1
    assert {"doc_id", "title", "snippet", "score", "tfidf_score", "pagerank_score"} <= set(
        search["results"][0]
    )

    doc_id = search["results"][0]["doc_id"]
    assert client.get(f"/documents/{doc_id}").status_code == 200
    assert client.get("/documents/missing").status_code == 404

