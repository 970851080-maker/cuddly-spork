from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NewsItem:
    title: str
    url: str
    source_id: str
    source_name: str
    credibility: int
    categories: list[str] = field(default_factory=list)
    region: str = "global"
    published_at: str | None = None  # ISO string if available
    content: str | None = None
    summary_zh: str | None = None
    is_new: bool | None = None
