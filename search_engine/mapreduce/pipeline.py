from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from search_engine.crawler import load_corpus
from search_engine.mapreduce.pagerank import compute_pagerank
from search_engine.mapreduce.tokenize import tokenize
from search_engine.parser import parse_document


def _normalize_link_ids(link: str) -> str:
    return link.replace(" ", "_").lower()


def build_index(
    corpus_dir: str | Path,
    limit: int | None = None,
    shards: int = 4,
    pagerank_iterations: int = 20,
) -> dict[str, Any]:
    raw_documents = load_corpus(corpus_dir, limit=limit)
    parsed_documents = [parse_document(raw) for raw in raw_documents]

    documents: dict[str, dict[str, Any]] = {}
    term_frequencies: dict[str, Counter[str]] = {}
    document_frequencies: Counter[str] = Counter()
    graph: dict[str, list[str]] = {}

    title_lookup = {
        doc.title.replace(" ", "_").lower(): doc.doc_id for doc in parsed_documents
    }

    for doc in parsed_documents:
        tokens = tokenize(f"{doc.title} {doc.text}")
        tf = Counter(tokens)
        term_frequencies[doc.doc_id] = tf
        document_frequencies.update(tf.keys())
        documents[doc.doc_id] = doc.as_record() | {
            "token_count": sum(tf.values()),
            "preview": doc.text[:320],
        }
        graph[doc.doc_id] = [
            title_lookup[link]
            for link in (_normalize_link_ids(link) for link in doc.links)
            if link in title_lookup and title_lookup[link] != doc.doc_id
        ]

    doc_count = len(documents)
    inverted_index: dict[str, list[dict[str, float | str]]] = defaultdict(list)

    for doc_id, tf in term_frequencies.items():
        token_total = sum(tf.values()) or 1
        for term, count in tf.items():
            term_frequency = count / token_total
            idf = math.log((1 + doc_count) / (1 + document_frequencies[term])) + 1
            inverted_index[term].append(
                {
                    "doc_id": doc_id,
                    "tf": term_frequency,
                    "idf": idf,
                    "weight": term_frequency * idf,
                }
            )

    pagerank = compute_pagerank(graph, iterations=pagerank_iterations)
    shard_map: dict[str, int] = {}
    for doc_id in documents:
        shard_map[doc_id] = hash(doc_id) % max(shards, 1)

    return {
        "metadata": {
            "document_count": doc_count,
            "term_count": len(inverted_index),
            "shard_count": shards,
            "pagerank_iterations": pagerank_iterations,
            "created_at": datetime.now(UTC).isoformat(),
        },
        "documents": documents,
        "inverted_index": dict(inverted_index),
        "pagerank": pagerank,
        "graph": graph,
        "shards": shard_map,
    }

