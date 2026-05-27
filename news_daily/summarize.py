from __future__ import annotations

import re

from .llm_translate import translate_to_zh
from .textutil import norm_space


_SENT_SPLIT = re.compile(r"(?<=[。！？!?])\\s+")


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


def summarize_zh(title: str, content: str | None, max_sentences: int = 2) -> str:
    content = _strip_html(content or "")
    if not content:
        return translate_to_zh(norm_space(title))
    sents = [s.strip() for s in _SENT_SPLIT.split(content) if s.strip()]
    picked = sents[:max_sentences] if sents else [content]
    summary = norm_space(" ".join(picked))
    if len(summary) > 180:
        summary = summary[:180].rstrip() + "…"
    return translate_to_zh(summary)
