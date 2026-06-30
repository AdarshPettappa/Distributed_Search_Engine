from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RawDocument:
    doc_id: str
    source_path: str
    html: str


@dataclass(frozen=True)
class ParsedDocument:
    doc_id: str
    title: str
    text: str
    links: list[str]
    source_path: str

    def as_record(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "text": self.text,
            "links": self.links,
            "source_path": self.source_path,
        }


@dataclass(frozen=True)
class SearchResult:
    doc_id: str
    title: str
    snippet: str
    score: float
    tfidf_score: float
    pagerank_score: float

