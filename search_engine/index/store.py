from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class IndexStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.index_path = self.root / "index.json"

    def save(self, index: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")

    def load(self) -> dict[str, Any]:
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Index not found at {self.index_path}. Run: python -m search_engine.cli ingest"
            )
        return json.loads(self.index_path.read_text(encoding="utf-8"))

