from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse


_SPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[【】\\[\\]（）()“”\"'‘’·•●◆■]|[，。！？；：、…]+")


def norm_space(s: str) -> str:
    return _SPACE_RE.sub(" ", (s or "").strip())


def norm_title(s: str) -> str:
    s = norm_space(s)
    s = _PUNCT_RE.sub(" ", s)
    s = s.lower()
    return norm_space(s)


def norm_url(url: str) -> str:
    try:
        p = urlparse(url)
        scheme = (p.scheme or "https").lower()
        netloc = p.netloc.lower()
        path = p.path or "/"
        return urlunparse((scheme, netloc, path, "", "", ""))
    except Exception:
        return (url or "").strip()

