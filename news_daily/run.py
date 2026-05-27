from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .classify import DOMAINS_12, enrich_domains
from .config import load_config
from .db import open_db
from .dedupe import is_near_duplicate
from .fetch.html import fetch_html_list
from .fetch.rss import fetch_rss
from .model import NewsItem
from .report import write_json, write_markdown
from .sources import load_sources
from .summarize import summarize_zh
from .textutil import norm_title, norm_url
from .timeutil import today_bjt_ymd


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _insert_if_new(db, item: NewsItem) -> bool:
    url_norm = norm_url(item.url)
    title_norm = norm_title(item.title)
    cur = db.conn.execute("SELECT title FROM items WHERE url_norm=?", (url_norm,))
    row = cur.fetchone()
    if row:
        return False
    # 额外的相似度去重：与最近 300 条做标题相似比对
    cur = db.conn.execute("SELECT title FROM items ORDER BY id DESC LIMIT 300")
    for (t,) in cur.fetchall():
        if is_near_duplicate(item.title, t):
            return False

    db.conn.execute(
        """
        INSERT INTO items(url,url_norm,title,title_norm,published_at,source_id,source_name,credibility,categories,region,summary_zh,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            item.url,
            url_norm,
            item.title,
            title_norm,
            item.published_at,
            item.source_id,
            item.source_name,
            int(item.credibility),
            ",".join(item.categories),
            item.region,
            item.summary_zh or "",
            _now_iso(),
        ),
    )
    return True


def generate_daily(date_str: str | None, sources_path: str) -> tuple[Path, Path]:
    cfg = load_config()
    date_ymd = date_str or today_bjt_ymd()
    sources = load_sources(sources_path)
    db = open_db(cfg.db_path)

    fetched: list[NewsItem] = []
    source_errors: list[dict] = []
    for s in sources:
        try:
            if s.type == "rss":
                fetched.extend(list(fetch_rss(s)))
            elif s.type == "html":
                fetched.extend(list(fetch_html_list(s, timeout_s=cfg.http_timeout_s)))
        except Exception as e:
            source_errors.append({"source_id": s.id, "url": s.url, "error": f"{type(e).__name__}: {e}"})

    # enrich + summarize
    for it in fetched:
        enrich_domains(it)
        it.summary_zh = summarize_zh(it.title, it.content)

    # de-duplicate within this run (keep "today's fetched" for report)
    report_items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for it in fetched:
        u = norm_url(it.url)
        if not u or u in seen_urls:
            continue
        # title similarity against already kept items
        if any(is_near_duplicate(it.title, x.title) for x in report_items[-200:]):
            continue
        seen_urls.add(u)
        report_items.append(it)

    # persist & record which are new (but report still includes existing)
    new_items: list[NewsItem] = []
    with db.conn:
        for it in report_items:
            is_new = _insert_if_new(db, it)
            it.is_new = is_new
            if is_new:
                new_items.append(it)

    # group by 12 domains (always present) - use report_items, not only new
    by_domain: dict[str, list[NewsItem]] = {d: [] for d in DOMAINS_12}
    for it in report_items:
        domains = [c for c in (it.categories or []) if c in by_domain]
        if not domains:
            domains = ["社会文化"]
        by_domain[domains[0]].append(it)

    items_by_domain = {d: by_domain[d] for d in DOMAINS_12}

    # focus lines (simple heuristic: policy/engineering + high credibility)
    focus = []
    for it in sorted(report_items, key=lambda x: (-x.credibility, x.published_at or ""))[:12]:
        focus.append(f"{it.title}（{it.source_name}）")

    md_path = cfg.output_dir / f"{date_ymd}.md"
    json_path = cfg.output_dir / f"{date_ymd}.json"
    meta = {
        "date_bjt": date_ymd,
        "generated_at_utc": _now_iso(),
        "sources_count": len(sources),
        "items": len(report_items),
        "new_items": len(new_items),
        "source_errors": source_errors,
        "run_env": {"github_actions": bool(os.getenv("GITHUB_ACTIONS"))},
    }
    write_markdown(md_path, date_ymd, items_by_domain, focus_lines=focus)
    write_json(json_path, report_items, meta=meta)
    return md_path, json_path


def send_daily(date_str: str) -> None:
    cfg = load_config()
    md_path = cfg.output_dir / f"{date_str}.md"
    json_path = cfg.output_dir / f"{date_str}.json"
    if not md_path.exists():
        raise FileNotFoundError(f"report not found: {md_path}")
    if json_path.exists():
        from .email_digest import build_email_body

        body = build_email_body(json_path)
        (cfg.output_dir / f"{date_str}.digest.md").write_text(body, encoding="utf-8")
    else:
        body = md_path.read_text(encoding="utf-8")
    subject = f"今日简报｜{date_str}"
    sent_or_configured = False

    # SMTP email (optional)
    if os.getenv("NEWS_DAILY_SMTP_HOST") and os.getenv("NEWS_DAILY_SMTP_USER") and os.getenv("NEWS_DAILY_SMTP_PASS") and os.getenv("NEWS_DAILY_EMAIL_TO"):
        from .notify.email_smtp import send_email

        send_email(subject=subject, body=body)
        sent_or_configured = True

    # Webhooks (optional)
    from .notify.webhook import post_feishu, post_wecom

    if os.getenv("NEWS_DAILY_FEISHU_WEBHOOK"):
        sent_or_configured = True
    post_feishu(body)
    if os.getenv("NEWS_DAILY_WECOM_WEBHOOK"):
        sent_or_configured = True
    post_wecom(body)
    if not sent_or_configured:
        raise RuntimeError("No notification channel configured. Set SMTP secrets or webhook environment variables.")
