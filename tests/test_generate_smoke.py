from pathlib import Path

import yaml

from news_daily.run import generate_daily


def test_generate_daily_smoke(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("NEWS_DAILY_DB_PATH", str(tmp_path / "db.sqlite3"))
    monkeypatch.setenv("NEWS_DAILY_OUTPUT_DIR", str(tmp_path / "out"))
    # minimal sources yaml with empty (disabled) to keep deterministic
    p = tmp_path / "sources.yaml"
    p.write_text(yaml.safe_dump({"sources": []}, allow_unicode=True), encoding="utf-8")
    md, js = generate_daily(date_str="2026-05-26", sources_path=str(p))
    assert md.exists()
    assert js.exists()

