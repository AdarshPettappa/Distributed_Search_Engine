from __future__ import annotations

import argparse
import json
from pathlib import Path

from search_engine.benchmark import run_benchmark
from search_engine.index import IndexStore
from search_engine.mapreduce import build_index


def ingest(args: argparse.Namespace) -> None:
    index = build_index(
        corpus_dir=args.corpus,
        limit=args.limit,
        shards=args.shards,
        pagerank_iterations=args.pagerank_iterations,
    )
    IndexStore(args.output).save(index)
    print(
        f"Indexed {index['metadata']['document_count']} documents, "
        f"{index['metadata']['term_count']} terms, {index['metadata']['shard_count']} shards."
    )


def benchmark(args: argparse.Namespace) -> None:
    result = run_benchmark(
        index_dir=args.index,
        queries=args.queries,
        runs=args.runs,
        workers=args.workers,
        output=args.output,
    )
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Distributed Wikipedia Search Engine")
    subcommands = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subcommands.add_parser("ingest", help="Build a TF-IDF + PageRank index")
    ingest_parser.add_argument("--corpus", default="data/sample_corpus")
    ingest_parser.add_argument("--output", default="data/index")
    ingest_parser.add_argument("--limit", type=int, default=None)
    ingest_parser.add_argument("--shards", type=int, default=4)
    ingest_parser.add_argument("--pagerank-iterations", type=int, default=20)
    ingest_parser.set_defaults(func=ingest)

    benchmark_parser = subcommands.add_parser("benchmark", help="Benchmark sequential vs threaded search")
    benchmark_parser.add_argument("--index", default="data/index")
    benchmark_parser.add_argument("--queries", nargs="+", default=["distributed search", "page rank"])
    benchmark_parser.add_argument("--runs", type=int, default=30)
    benchmark_parser.add_argument("--workers", type=int, default=4)
    benchmark_parser.add_argument("--output", default=Path("results") / "benchmark_results.json")
    benchmark_parser.set_defaults(func=benchmark)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

