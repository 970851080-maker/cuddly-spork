from __future__ import annotations

import random

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; news-daily-bot/0.1; +https://github.com/)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@retry(
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.6, min=0.6, max=5),
)
def get(url: str, timeout_s: int) -> requests.Response:
    headers = dict(DEFAULT_HEADERS)
    headers["User-Agent"] = headers["User-Agent"] + f" r{random.randint(1000,9999)}"
    resp = requests.get(url, headers=headers, timeout=timeout_s)
    resp.raise_for_status()
    return resp
