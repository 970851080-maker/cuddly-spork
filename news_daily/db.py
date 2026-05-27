from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL,
  url_norm TEXT NOT NULL,
  title TEXT NOT NULL,
  title_norm TEXT NOT NULL,
  published_at TEXT,
  source_id TEXT NOT NULL,
  source_name TEXT NOT NULL,
  credibility INTEGER NOT NULL,
  categories TEXT NOT NULL,
  region TEXT NOT NULL,
  summary_zh TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_items_url_norm ON items(url_norm);
"""


@dataclass(frozen=True)
class Db:
    conn: sqlite3.Connection


def open_db(path: Path) -> Db:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path.as_posix())
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(SCHEMA_SQL)
    return Db(conn=conn)

