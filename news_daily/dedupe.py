from __future__ import annotations

from rapidfuzz import fuzz

from .textutil import norm_title


def is_near_duplicate(title_a: str, title_b: str, threshold: int = 92) -> bool:
    a = norm_title(title_a)
    b = norm_title(title_b)
    if not a or not b:
        return False
    score = fuzz.token_set_ratio(a, b)
    return score >= threshold

