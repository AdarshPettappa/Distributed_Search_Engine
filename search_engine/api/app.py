from __future__ import annotations

import os
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Query

from search_engine.index import IndexStore
from search_engine.index.search import SearchEngine


def create_app() -> FastAPI:
    index_dir = os.getenv("SEARCH_INDEX_DIR", "data/index")
    index = IndexStore(index_dir).load()
    engine = SearchEngine(index)
    app = FastAPI(
        title="Distributed Wikipedia Search Engine",
        version="0.1.0",
        description="TF-IDF + PageRank search over a locally sharded Wikipedia-style index.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/stats")
    def stats() -> dict[str, object]:
        return index["metadata"]

    @app.get("/search")
    def search(
        q: str = Query(..., min_length=1),
        k: int = Query(10, ge=1, le=50),
        workers: int = Query(4, ge=1, le=32),
    ) -> dict[str, object]:
        results = engine.search_threaded(q, k=k, workers=workers)
        return {"query": q, "count": len(results), "results": [asdict(result) for result in results]}

    @app.get("/documents/{doc_id}")
    def document(doc_id: str) -> dict[str, object]:
        doc = index["documents"].get(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    return app

