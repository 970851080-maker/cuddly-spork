from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UserProfile:
    display_name: str | None = None
    birth_year: int | None = None
    birth_place: str | None = None
    current_role: str | None = None
    current_city: str | None = None
    next_city: str | None = None
    take_home_monthly_cny: int | None = None
    debt_cny: int | None = None


def _to_int(v: Any) -> int | None:
    try:
        if v is None:
            return None
        return int(v)
    except Exception:
        return None


def load_user_profile() -> UserProfile | None:
    """
    Loads a lightweight personal profile from env.

    Expected env:
      - NEWS_DAILY_USER_PROFILE_JSON: JSON string
    """
    raw = os.getenv("NEWS_DAILY_USER_PROFILE_JSON")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    return UserProfile(
        display_name=data.get("display_name"),
        birth_year=_to_int(data.get("birth_year")),
        birth_place=data.get("birth_place"),
        current_role=data.get("current_role"),
        current_city=data.get("current_city"),
        next_city=data.get("next_city"),
        take_home_monthly_cny=_to_int(data.get("take_home_monthly_cny")),
        debt_cny=_to_int(data.get("debt_cny")),
    )

