from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    db_path: Path
    output_dir: Path
    http_timeout_s: int


def load_config() -> AppConfig:
    db_path = Path(os.getenv("NEWS_DAILY_DB_PATH", "output/news_daily.sqlite3"))
    output_dir = Path(os.getenv("NEWS_DAILY_OUTPUT_DIR", "output/daily"))
    http_timeout_s = int(os.getenv("NEWS_DAILY_HTTP_TIMEOUT", "15"))
    return AppConfig(db_path=db_path, output_dir=output_dir, http_timeout_s=http_timeout_s)

