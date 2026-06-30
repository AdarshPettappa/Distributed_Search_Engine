from __future__ import annotations

import re
from pathlib import PurePosixPath
from urllib.parse import unquote

from bs4 import BeautifulSoup

from search_engine.models import ParsedDocument, RawDocument


SPACE_RE = re.compile(r"\s+")


def _clean(value: str) -> str:
    return SPACE_RE.sub(" ", value).strip()


def _link_to_doc_id(href: str) -> str | None:
    if not href:
        return None
    target = href.split("#", 1)[0].split("?", 1)[0].strip("/")
    if not target:
        return None
    target = unquote(target).split("/")[-1]
    target = PurePosixPath(target).stem
    return target.replace(" ", "_").lower()


def parse_document(raw: RawDocument) -> ParsedDocument:
    soup = BeautifulSoup(raw.html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title_node = soup.find("title") or soup.find(["h1", "h2"])
    title = _clean(title_node.get_text(" ")) if title_node else raw.doc_id
    text = _clean(soup.get_text(" "))

    links: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a"):
        doc_id = _link_to_doc_id(anchor.get("href", ""))
        if doc_id and doc_id not in seen:
            links.append(doc_id)
            seen.add(doc_id)

    return ParsedDocument(
        doc_id=raw.doc_id,
        title=title,
        text=text,
        links=links,
        source_path=raw.source_path,
    )
