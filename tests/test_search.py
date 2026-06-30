from pathlib import Path

from search_engine.index.search import SearchEngine
from search_engine.mapreduce import build_index


def test_search_ranks_matching_documents():
    engine = SearchEngine(build_index(Path("data/sample_corpus"), shards=4))

    results = engine.search_threaded("distributed search", k=3)

    assert results
    assert results[0].title == "Distributed Search"
    assert results[0].tfidf_score > 0
    assert results[0].pagerank_score >= 0
    assert results[0].snippet

