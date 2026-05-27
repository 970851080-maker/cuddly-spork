from __future__ import annotations

import re
from typing import Any, Iterable


_CSCEC3B3_KEYWORDS = [
    "中建三局第三建设工程有限责任公司",
    "中建三局第三建设",
    "中建三局三公司",
    "中建三局第三公司",
    "三局三公司",
]

_BID_KEYWORDS = [
    "招标",
    "投标",
    "中标",
    "候选人",
    "公示",
    "采购",
    "暂停",
    "处理",
    "禁入",
]


def _get(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _text(item: Any) -> str:
    title = (_get(item, "title", "") or "").strip()
    summary = (_get(item, "summary_zh", "") or "").strip()
    src = (_get(item, "source_name", "") or "").strip()
    return f"{title} {summary} {src}".strip()


def extract_cscec3b3_tender_updates(items: Iterable[Any], limit: int = 6) -> list[dict[str, str]]:
    """
    Best-effort extraction from the already-fetched items set.
    Returns list of {title, url, source_name}.
    """
    hits: list[dict[str, str]] = []
    seen: set[str] = set()

    for it in items:
        title = (_get(it, "title", "") or "").strip()
        url = (_get(it, "url", "") or "").strip()
        src = (_get(it, "source_name", "") or "").strip()
        text = _text(it)
        if not title or not url:
            continue
        if url in seen:
            continue

        company_hit = any(k in text for k in _CSCEC3B3_KEYWORDS)
        bid_hit = any(k in text for k in _BID_KEYWORDS)

        # Also catch "三局三公司" like mentions with digits/abbrev variations.
        if not company_hit:
            if re.search(r"三局.{0,3}三公司", text):
                company_hit = True

        if company_hit and bid_hit:
            seen.add(url)
            hits.append({"title": title, "url": url, "source_name": src})
            if len(hits) >= limit:
                break

    return hits

