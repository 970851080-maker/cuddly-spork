from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    type: str  # rss | html
    url: str
    categories: list[str]
    region: str
    credibility: int
    enabled: bool = True
    max_items: int = 20


def load_sources(path: str | Path) -> list[Source]:
    p = Path(path)
    data: dict[str, Any] = yaml.safe_load(p.read_text(encoding="utf-8"))
    raw_sources = data.get("sources", [])
    sources: list[Source] = []
    for s in raw_sources:
        sources.append(
            Source(
                id=str(s["id"]),
                name=str(s["name"]),
                type=str(s["type"]),
                url=str(s["url"]),
                categories=list(s.get("categories") or []),
                region=str(s.get("region") or "global"),
                credibility=int(s.get("credibility") or 3),
                enabled=bool(s.get("enabled", True)),
                max_items=int(s.get("max_items") or 20),
            )
        )
    return [s for s in sources if s.enabled]
