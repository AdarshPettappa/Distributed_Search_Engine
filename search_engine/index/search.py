from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Any, Iterable

from search_engine.mapreduce.tokenize import tokenize
from search_engine.models import SearchResult


class SearchEngine:
    def __init__(self, index: dict[str, Any]):
        self.index = index
        self.documents = index["documents"]
        self.inverted_index = index["inverted_index"]
        self.pagerank = index["pagerank"]
        self.shards = index["shards"]
        self.shard_ids = sorted(set(self.shards.values()))

    def _snippet(self, doc: dict[str, Any], terms: Iterable[str]) -> str:
        text = doc.get("text", "")
        lower = text.lower()
        first_hit = min((lower.find(term) for term in terms if lower.find(term) >= 0), default=0)
        start = max(first_hit - 60, 0)
        return text[start : start + 220].strip()

    def _search_shard(self, query_terms: list[str], shard_id: int) -> dict[str, float]:
        scores: dict[str, float] = defaultdict(float)
        for term in query_terms:
            for posting in self.inverted_index.get(term, []):
                doc_id = posting["doc_id"]
                if self.shards.get(doc_id) == shard_id:
                    scores[doc_id] += float(posting["weight"])
        return scores

    def search_sequential(self, query: str, k: int = 10) -> list[SearchResult]:
        query_terms = tokenize(query)
        merged: dict[str, float] = defaultdict(float)
        for shard_id in self.shard_ids:
            for doc_id, score in self._search_shard(query_terms, shard_id).items():
                merged[doc_id] += score
        return self._rank(query_terms, merged, k)

    def search_threaded(self, query: str, k: int = 10, workers: int = 4) -> list[SearchResult]:
        query_terms = tokenize(query)
        merged: dict[str, float] = defaultdict(float)
        if not query_terms:
            return []

        max_workers = max(1, min(workers, len(self.shard_ids) or 1))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._search_shard, query_terms, shard_id)
                for shard_id in self.shard_ids
            ]
            for future in futures:
                for doc_id, score in future.result().items():
                    merged[doc_id] += score
        return self._rank(query_terms, merged, k)

    def _rank(self, query_terms: list[str], tfidf_scores: dict[str, float], k: int) -> list[SearchResult]:
        ranked: list[SearchResult] = []
        max_pr = max(self.pagerank.values(), default=1.0) or 1.0
        for doc_id, tfidf_score in tfidf_scores.items():
            doc = self.documents[doc_id]
            pagerank_score = self.pagerank.get(doc_id, 0.0) / max_pr
            score = (0.82 * tfidf_score) + (0.18 * pagerank_score)
            ranked.append(
                SearchResult(
                    doc_id=doc_id,
                    title=doc["title"],
                    snippet=self._snippet(doc, query_terms),
                    score=round(score, 6),
                    tfidf_score=round(tfidf_score, 6),
                    pagerank_score=round(pagerank_score, 6),
                )
            )
        return sorted(ranked, key=lambda item: item.score, reverse=True)[:k]

