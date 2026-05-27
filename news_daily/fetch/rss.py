from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

import feedparser

from ..model import NewsItem
from ..sources import Source
from ..textutil import norm_space


def _strip_html(s: str) -> str:
    s = (s or "").replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    while "<" in s and ">" in s:
        start = s.find("<")
        end = s.find(">", start + 1)
        if start >= 0 and end > start:
            s = s[:start] + " " + s[end + 1 :]
        else:
            break
    return norm_space(s)


def _published_iso(entry) -> str | None:
    for key in ("published_parsed", "updated_parsed"):
        t = getattr(entry, key, None)
        if t:
            return datetime(*t[:6]).isoformat()
    return None


def _is_recent(entry, days: int = 45) -> bool:
    for key in ("published_parsed", "updated_parsed"):
        t = getattr(entry, key, None)
        if t:
            dt = datetime(*t[:6], tzinfo=timezone.utc)
            return dt >= datetime.now(tz=timezone.utc) - timedelta(days=days)
    return True


def fetch_rss(source: Source) -> Iterable[NewsItem]:
    feed = feedparser.parse(source.url)
    yielded = 0
    for e in feed.entries or []:
        if not _is_recent(e):
            continue
        title = norm_space(getattr(e, "title", "") or "")
        url = norm_space(getattr(e, "link", "") or "")
        if not title or not url:
            continue
        yielded += 1
        yield NewsItem(
            title=title,
            url=url,
            source_id=source.id,
            source_name=source.name,
            credibility=source.credibility,
            categories=list(source.categories),
            region=source.region,
            published_at=_published_iso(e),
            content=_strip_html(getattr(e, "summary", "") or ""),
        )
        if yielded >= source.max_items:
            break
