from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import requests


_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_CACHE: dict[str, str] = {}
_CALLS = 0


def looks_chinese(text: str, min_cjk: int = 3) -> bool:
    if not text:
        return True
    return len(_CJK_RE.findall(text)) >= min_cjk


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    base_url: str
    model: str
    timeout_s: int = 30


def load_openai_config() -> OpenAIConfig | None:
    api_key = os.getenv("OPENAI_API_KEY") or ""
    if not api_key:
        return None
    base_url = (os.getenv("OPENAI_BASE_URL") or "https://api.openai.com").rstrip("/")
    model = os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"
    timeout_s = int(os.getenv("OPENAI_TIMEOUT_S") or "30")
    return OpenAIConfig(api_key=api_key, base_url=base_url, model=model, timeout_s=timeout_s)


def translate_to_zh(text: str) -> str:
    """
    Best-effort translation to Simplified Chinese.
    Uses OpenAI only if OPENAI_API_KEY is set; otherwise returns original.
    """
    text = (text or "").strip()
    if not text:
        return ""
    if looks_chinese(text):
        return text
    cached = _CACHE.get(text)
    if cached is not None:
        return cached

    cfg = load_openai_config()
    if cfg is None:
        return text
    global _CALLS
    max_calls = int(os.getenv("OPENAI_TRANSLATE_MAX_CALLS") or "40")
    if _CALLS >= max_calls:
        _CACHE[text] = text
        return text

    url = f"{cfg.base_url}/v1/responses"
    headers = {"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"}
    payload = {
        "model": cfg.model,
        "input": [
            {
                "role": "system",
                "content": (
                    "You are a professional bilingual editor. "
                    "Translate the user text into concise, natural Simplified Chinese. "
                    "Keep proper nouns and organizations accurate; do not add facts. "
                    "Output Chinese only."
                ),
            },
            {"role": "user", "content": text},
        ],
    }
    try:
        _CALLS += 1
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=cfg.timeout_s)
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as e:
        # Never fail the whole daily run due to translation throttling.
        if getattr(e.response, "status_code", None) in (429, 500, 502, 503, 504):
            _CACHE[text] = text
            return text
        raise

    # responses API: prefer output_text when present, else walk output array.
    out = (data.get("output_text") or "").strip()
    if out:
        _CACHE[text] = out
        return out
    chunks: list[str] = []
    for item in data.get("output") or []:
        for c in item.get("content") or []:
            if c.get("type") == "output_text" and c.get("text"):
                chunks.append(c["text"])
    out2 = ("".join(chunks)).strip() or text
    _CACHE[text] = out2
    return out2
