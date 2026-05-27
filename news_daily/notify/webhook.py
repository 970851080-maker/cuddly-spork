from __future__ import annotations

import os

import requests


def post_feishu(markdown_text: str) -> None:
    url = os.getenv("NEWS_DAILY_FEISHU_WEBHOOK")
    if not url:
        return
    payload = {"msg_type": "text", "content": {"text": markdown_text[:19000]}}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()


def post_wecom(markdown_text: str) -> None:
    url = os.getenv("NEWS_DAILY_WECOM_WEBHOOK")
    if not url:
        return
    payload = {"msgtype": "text", "text": {"content": markdown_text[:19000]}}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

