from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any

from search_engine.index import IndexStore
from search_engine.index.search import SearchEngine


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(round((percentile / 100) * (len(ordered) - 1)), len(ordered) - 1)
    return ordered[index]


def run_benchmark(
    index_dir: str | Path,
    queries: list[str],
    runs: int = 30,
    workers: int = 4,
    output: str | Path = "results/benchmark_results.json",
) -> dict[str, Any]:
    engine = SearchEngine(IndexStore(index_dir).load())
    sequential_ms: list[float] = []
    threaded_ms: list[float] = []

    for _ in range(runs):
        for query in queries:
            start = time.perf_counter()
            engine.search_sequential(query)
            sequential_ms.append((time.perf_counter() - start) * 1000)

            start = time.perf_counter()
            engine.search_threaded(query, workers=workers)
            threaded_ms.append((time.perf_counter() - start) * 1000)

    seq_avg = statistics.mean(sequential_ms) if sequential_ms else 0.0
    threaded_avg = statistics.mean(threaded_ms) if threaded_ms else 0.0
    improvement = ((seq_avg - threaded_avg) / seq_avg * 100) if seq_avg else 0.0

    result = {
        "queries": queries,
        "runs_per_query": runs,
        "workers": workers,
        "sequential": {
            "avg_ms": round(seq_avg, 3),
            "p50_ms": round(_percentile(sequential_ms, 50), 3),
            "p95_ms": round(_percentile(sequential_ms, 95), 3),
        },
        "threaded": {
            "avg_ms": round(threaded_avg, 3),
            "p50_ms": round(_percentile(threaded_ms, 50), 3),
            "p95_ms": round(_percentile(threaded_ms, 95), 3),
        },
        "latency_reduction_percent": round(improvement, 2),
    }
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

