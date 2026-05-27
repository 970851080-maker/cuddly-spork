from __future__ import annotations

from datetime import datetime, timedelta, timezone


TZ_BJT = timezone(timedelta(hours=8))


def today_bjt_ymd() -> str:
    return datetime.now(tz=TZ_BJT).strftime("%Y-%m-%d")


def parse_ymd_bjt(date_str: str) -> datetime:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.replace(tzinfo=TZ_BJT)

