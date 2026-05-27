from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .classify import DOMAIN_REPRESENTATIVES, DOMAINS_12
from .model import NewsItem
from .personal_analysis import build_personal_insights


def credibility_label(score: int) -> str:
    if score >= 5:
        return "很高"
    if score == 4:
        return "较高"
    if score == 3:
        return "中等"
    if score == 2:
        return "较低"
    return "低"


def write_json(path: Path, items: list[NewsItem], meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"meta": meta, "items": [asdict(i) for i in items]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _strip_html(s: str) -> str:
    s = s.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    while "<" in s and ">" in s:
        start = s.find("<")
        end = s.find(">", start + 1)
        if start >= 0 and end > start:
            s = s[:start] + " " + s[end + 1 :]
        else:
            break
    return " ".join(s.split())


def write_markdown(path: Path, date_ymd: str, items_by_cat: dict[str, list[NewsItem]], focus_lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append(f"# 晨间新闻日报｜{date_ymd}")
    lines.append("")
    lines.append("## 今早最值得关注")
    for x in focus_lines[:5]:
        lines.append(f"- {x}")
    if not focus_lines:
        lines.append("- （暂无）")
    lines.append("")
    lines.append("## 新闻联播要点（抓取到则展示）")
    xwlb_items = []
    for items in items_by_cat.values():
        for it in items:
            if it.source_id == "cctv_xwlb" or "新闻联播" in it.title:
                xwlb_items.append(it)
    if xwlb_items:
        for it in xwlb_items[:12]:
            lines.append(f"- {_strip_html(it.title)}（{it.source_name}）  \n  原文：{it.url}")
    else:
        lines.append("- （未抓取到新闻联播条目：可能源站改版/反爬；可在 sources.yaml 里调整央视源）")
    lines.append("")
    lines.append("## 主要内容摘要")
    for domain in DOMAINS_12:
        reps = DOMAIN_REPRESENTATIVES.get(domain, {})
        world = "、".join(reps.get("world", []))
        china = "、".join(reps.get("china", []))
        lines.append(f"### {domain}")
        if world or china:
            lines.append(f"- 世界顶尖代表：{world or '—'}")
            lines.append(f"- 中国顶尖代表：{china or '—'}")
        items = items_by_cat.get(domain, []) or []
        if not items:
            lines.append("- （暂无显著更新）")
            lines.append("")
            continue
        for it in items[:15]:
            cred = credibility_label(it.credibility)
            src = it.source_name
            summ = _strip_html(it.summary_zh or it.title)
            lines.append(f"- {summ}（来源：{src}｜可信度：{cred}）  \n  原文：{it.url}")
        lines.append("")
    lines.append("## 时间线/关键信息")
    timeline = []
    for cat_items in items_by_cat.values():
        for it in cat_items:
            if it.published_at:
                timeline.append((it.published_at, it))
    timeline.sort(key=lambda x: x[0])
    if timeline:
        for ts, it in timeline[:30]:
            lines.append(f"- {ts}｜{it.title}（{it.source_name}）")
    else:
        lines.append("- （多数来源未提供时间戳，略）")
    lines.append("")
    lines.append("## 后续关注")
    lines.append("- 关注住建部/发改委/财政部/交通运输部是否有新政策、资金或项目清单发布。")
    lines.append("- 关注基建/房地产/城市更新项目落地与融资环境变化。")
    lines.append("- 关注山西太原、武汉、哈尔滨相关重大项目、招投标、规划与交通建设动态。")
    lines.append("")
    lines.append("## 和我有什么关系（大白话）")
    all_items = [it for items in items_by_cat.values() for it in items]
    for insight in build_personal_insights(all_items):
        lines.append(f"- {insight}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
