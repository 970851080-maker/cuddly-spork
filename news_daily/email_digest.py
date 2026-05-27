from __future__ import annotations

import json
import os
from pathlib import Path

from .classify import DOMAINS_12
from .personal_analysis import build_personal_insights
from .personal_growth import build_personal_growth
from .tender_watch import extract_cscec3b3_tender_updates
from .user_profile import load_user_profile


def build_email_body(json_path: Path, max_per_domain: int = 4) -> str:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    meta = data.get("meta") or {}
    items: list[dict] = data.get("items") or []
    date_ymd = meta.get("date_bjt") or json_path.stem

    groups: dict[str, list[dict]] = {d: [] for d in DOMAINS_12}
    xwlb: list[dict] = []
    for it in items:
        cats = it.get("categories") or []
        domain = next((c for c in cats if c in groups), "社会文化")
        groups[domain].append(it)
        if it.get("source_id") == "cctv_xwlb" or "新闻联播" in (it.get("title") or ""):
            xwlb.append(it)

    profile = load_user_profile()
    growth = build_personal_growth(profile)
    tender_updates = extract_cscec3b3_tender_updates(items, limit=6)

    def _fmt_zh(it: dict) -> str:
        summary = it.get("summary_zh") or it.get("title") or ""
        src = it.get("source_name") or ""
        cred = it.get("credibility")
        url = it.get("url") or ""
        new_flag = "｜新增" if it.get("is_new") else ""
        return f"- {summary}（来源：{src}｜可信度：{cred}{new_flag}）\n  链接：{url}"

    def _fmt_en(it: dict) -> str:
        summary = it.get("summary_zh") or it.get("title") or ""
        src = it.get("source_name") or ""
        cred = it.get("credibility")
        url = it.get("url") or ""
        new_flag = " (new)" if it.get("is_new") else ""
        return f"- {summary} (Source: {src}; Credibility: {cred}{new_flag})\n  Link: {url}"

    # English (best-effort)
    en: list[str] = []
    en.append(f"# Daily Brief | {date_ymd}")
    en.append("")
    en.append("## Immediate attention")
    en.append("- This GitHub Actions workflow sends the email from the cloud, so your PC can be off.")
    en.append("- Calendar + unread-email summaries are not included here (OAuth not configured).")
    en.append("")
    en.append("## Personal development (plain talk)")
    for line in growth.get("en") or []:
        en.append(f"- {line}")
    en.append("")
    en.append("## CSCEC 3rd Bureau 3rd Company | Latest tenders/bids (public signals)")
    if tender_updates:
        for it in tender_updates:
            en.append(f"- {it['title']}\n  Source: {it.get('source_name','')}\n  Link: {it['url']}")
    else:
        en.append("- (No matching tender/bid signals found in today’s fetched set.)")
    en.append("")
    en.append("## CCTV Xinwen Lianbo highlights (Top 10)")
    if xwlb:
        for it in xwlb[:10]:
            en.append(f"- {it.get('title')}\n  Link: {it.get('url')}")
    else:
        en.append("- (Not captured today.)")
    en.append("")
    en.append("## News by domain (Top items)")
    for d in DOMAINS_12:
        en.append(f"### {d}")
        xs = groups.get(d) or []
        if not xs:
            en.append("- (No notable updates.)")
            en.append("")
            continue
        for it in xs[:max_per_domain]:
            en.append(_fmt_en(it))
        en.append("")
    en.append("## How this relates to me (plain talk)")
    for insight in build_personal_insights(items):
        en.append(f"- {insight}")
    en.append("")

    # Chinese
    zh: list[str] = []
    zh.append(f"# 今日简报｜{date_ymd}")
    zh.append("")
    zh.append(f"- 抓取条目：{meta.get('items', len(items))}｜新增入库：{meta.get('new_items', 0)}")
    zh.append("")
    zh.append("## 需要立即注意")
    zh.append("- 本邮件由 GitHub Actions（云端定时）发送，你电脑关机也能收到。")
    zh.append("- 当前工作流不包含“日历/未读邮件”汇总（未配置 OAuth）。")
    zh.append("")
    zh.append("## 个人发展（大白话+逻辑分析）")
    for line in growth.get("zh") or []:
        zh.append(f"- {line}")
    zh.append("")
    zh.append("## 中建三局三公司｜最新招投标/中标动态（公开信号）")
    if tender_updates:
        for it in tender_updates:
            zh.append(f"- {it['title']}  \n  来源：{it.get('source_name','')}  \n  链接：{it['url']}")
    else:
        zh.append("- （今天抓取集合里未检索到匹配“中建三局三公司+招投标/中标/公示”等关键词的条目）")
    zh.append("")
    zh.append("## 新闻联播要点（Top 10）")
    if xwlb:
        for it in xwlb[:10]:
            zh.append(f"- {it.get('title')}  \n  原文：{it.get('url')}")
    else:
        zh.append("- （未抓取到）")
    zh.append("")
    zh.append("## 12个领域动向（每类Top条目）")
    for d in DOMAINS_12:
        zh.append(f"### {d}")
        xs = groups.get(d) or []
        if not xs:
            zh.append("- （暂无显著更新）")
            zh.append("")
            continue
        for it in xs[:max_per_domain]:
            zh.append(_fmt_zh(it))
        zh.append("")
    zh.append("## 和我有什么关系（大白话）")
    for insight in build_personal_insights(items):
        zh.append(f"- {insight}")
    zh.append("")

    separator = os.getenv("NEWS_DAILY_BILINGUAL_SEPARATOR", "\n\n---\n\n")
    return "\n".join(en) + separator + "\n".join(zh)

