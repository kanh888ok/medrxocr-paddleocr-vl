"""Text helpers shared by evaluation and demos."""

from __future__ import annotations

import re


def normalize_text(text: str | None) -> str:
    text = "" if text is None else str(text)
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)


def length_bin(text: str | None) -> str:
    n = len(normalize_text(text))
    if n <= 4:
        return "short_0_4"
    if n <= 8:
        return "medium_5_8"
    if n <= 16:
        return "long_9_16"
    return "very_long_17_plus"


def has_digit(text: str | None) -> bool:
    return any(ch.isdigit() for ch in normalize_text(text))


def digits_only(text: str | None) -> str:
    return "".join(ch for ch in normalize_text(text) if ch.isdigit())
