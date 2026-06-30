from __future__ import annotations

import hashlib
from pathlib import Path

from search_engine.models import RawDocument


SUPPORTED_SUFFIXES = {".html", ".htm", ".xml", ".txt"}


def stable_doc_id(path: Path) -> str:
    return hashlib.sha1(path.stem.encode("utf-8")).hexdigest()[:12]


def load_corpus(corpus_dir: str | Path, limit: int | None = None) -> list[RawDocument]:
    root = Path(corpus_dir)
    if not root.exists():
        raise FileNotFoundError(f"Corpus directory does not exist: {root}")

    documents: list[RawDocument] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        documents.append(
            RawDocument(
                doc_id=stable_doc_id(path),
                source_path=str(path),
                html=path.read_text(encoding="utf-8"),
            )
        )
        if limit is not None and len(documents) >= limit:
            break
    return documents

