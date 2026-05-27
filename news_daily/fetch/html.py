from __future__ import annotations

from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..model import NewsItem
from ..sources import Source
from ..textutil import norm_space
from .http import get


NAV_TITLES = {
    "about",
    "about fao",
    "accessibility",
    "contact",
    "events",
    "home",
    "get involved",
    "ar",
    "esg-投资者关系-信息公开",
    "中建集团学习贯彻习近平新时代中国特色社会主义思想主题教育",
    "“建证·清风”中建集团纪检监察专题网站",
    "基础设施建设与投资",
    "数字能源业务网站",
    "房地产投资与开发",
    "in action",
    "main topics",
    "media",
    "member countries",
    "menu",
    "news",
    "newsletter",
    "press",
    "privacy",
    "search",
    "subscribe",
    "topics",
    "what we do",
    "who we are",
    "中文",
    "专题",
    "业务",
    "产品",
    "信息公开",
    "关于我们",
    "联系我们",
    "更多",
    "机构",
    "栏目",
    "检索",
    "目录",
    "网站地图",
    "首页",
}


def _looks_like_nav(title: str) -> bool:
    normalized = norm_space(title).strip(" -|·•").lower()
    if normalized in NAV_TITLES:
        return True
    return any(x in normalized for x in ["投资者关系", "信息公开", "网站地图", "language", "cookie"])


def fetch_html_list(source: Source, timeout_s: int) -> Iterable[NewsItem]:
    resp = get(source.url, timeout_s=timeout_s)
    resp.encoding = resp.apparent_encoding or "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # Per-source heuristics to reduce navigation noise.
    if source.id == "cctv_xwlb":
        anchors = soup.select('a[href*="/VIDE"]')
    else:
        anchors = soup.select("a[href]")

    yielded = 0
    for a in anchors[:400]:
        href = a.get("href") or ""
        title = norm_space(a.get_text(" ", strip=True))
        if not title or len(title) < 8:
            continue
        if _looks_like_nav(title):
            continue
        if source.id == "cctv_xwlb" and ("完整版" not in title and "新闻联播" not in title and "[视频]" not in title):
            continue
        if href.startswith("javascript:") or href.startswith("#"):
            continue
        url = urljoin(source.url, href)
        yielded += 1
        yield NewsItem(
            title=title,
            url=url,
            source_id=source.id,
            source_name=source.name,
            credibility=source.credibility,
            categories=list(source.categories),
            region=source.region,
        )
        if yielded >= source.max_items:
            break
