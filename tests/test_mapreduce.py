from pathlib import Path

from search_engine.mapreduce import build_index
from search_engine.mapreduce.pagerank import compute_pagerank
from search_engine.mapreduce.tokenize import tokenize


def test_tokenizer_normalizes_and_removes_stopwords():
    assert tokenize("The Distributed SEARCH, and API!") == ["distributed", "search", "api"]


def test_build_index_contains_expected_terms_and_postings():
    index = build_index(Path("data/sample_corpus"), shards=3)

    assert index["metadata"]["document_count"] == 6
    assert "search" in index["inverted_index"]
    assert len(index["inverted_index"]["search"]) >= 2
    assert index["metadata"]["shard_count"] == 3


def test_pagerank_converges_and_normalizes():
    ranks = compute_pagerank({"a": ["b"], "b": ["c"], "c": ["b"]}, iterations=30)

    assert round(sum(ranks.values()), 6) == 1.0
    assert ranks["b"] > ranks["a"]

