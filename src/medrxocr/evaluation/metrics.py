"""Shared OCR metrics."""

from __future__ import annotations

from collections import Counter
from typing import Any

from medrxocr.utils.text import digits_only, has_digit, normalize_text


def edit_distance(prediction: str | None, gold: str | None) -> int:
    pred = normalize_text(prediction)
    truth = normalize_text(gold)
    prev = list(range(len(truth) + 1))
    for i, pred_ch in enumerate(pred, 1):
        cur = [i]
        for j, truth_ch in enumerate(truth, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (pred_ch != truth_ch)))
        prev = cur
    return prev[-1]


def text_cer(prediction: str | None, gold: str | None) -> float:
    truth = normalize_text(gold)
    return edit_distance(prediction, gold) / max(len(truth), 1)


def exact_match(prediction: str | None, gold: str | None) -> bool:
    return normalize_text(prediction) == normalize_text(gold)


def char_error_breakdown(prediction: str | None, gold: str | None) -> dict[str, int]:
    pred = normalize_text(prediction)
    truth = normalize_text(gold)
    rows = len(pred) + 1
    cols = len(truth) + 1
    dp = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        dp[i][0] = i
    for j in range(cols):
        dp[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + (pred[i - 1] != truth[j - 1]),
            )

    i, j = len(pred), len(truth)
    counts = Counter({"matches": 0, "substitutions": 0, "insertions": 0, "deletions": 0})
    while i > 0 or j > 0:
        if i > 0 and j > 0 and pred[i - 1] == truth[j - 1] and dp[i][j] == dp[i - 1][j - 1]:
            counts["matches"] += 1
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            counts["substitutions"] += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            counts["insertions"] += 1
            i -= 1
        else:
            counts["deletions"] += 1
            j -= 1
    counts["edit_distance"] = dp[-1][-1]
    return dict(counts)


def word_ocr_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if row.get("cer") is not None]
    total_dist = 0
    total_chars = 0
    for row in valid:
        pred = row.get("prediction", {}).get("full_ocr_text", "")
        gold = row.get("gold_text", "")
        total_dist += int(row.get("edit_distance") if row.get("edit_distance") is not None else edit_distance(pred, gold))
        total_chars += int(row.get("gold_chars") if row.get("gold_chars") is not None else max(len(normalize_text(gold)), 1))
    digit_rows = [row for row in valid if has_digit(row.get("gold_text"))]
    return {
        "n_records": len(rows),
        "n_scored": len(valid),
        "errors": sum(1 for row in rows if row.get("error")),
        "exact_match_rate": sum(1 for row in valid if row.get("exact_match")) / len(valid) if valid else None,
        "mean_cer": sum(float(row["cer"]) for row in valid) / len(valid) if valid else None,
        "micro_cer": total_dist / total_chars if total_chars else None,
        "digit_record_count": len(digit_rows),
        "digit_exact_rate": (
            sum(1 for row in digit_rows if digits_only(row.get("prediction", {}).get("full_ocr_text")) == digits_only(row.get("gold_text")))
            / len(digit_rows)
            if digit_rows
            else None
        ),
    }
