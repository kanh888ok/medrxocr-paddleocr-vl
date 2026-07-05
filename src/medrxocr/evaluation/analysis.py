"""Error and latency analysis for OCR predictions."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median
from typing import Any

from medrxocr.evaluation.metrics import char_error_breakdown, word_ocr_summary
from medrxocr.utils.text import digits_only, has_digit, length_bin


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round((len(values) - 1) * q)))
    return values[idx]


def analyze_predictions(rows: list[dict[str, Any]], slow_threshold_sec: float = 10.0) -> dict[str, Any]:
    scored = [row for row in rows if row.get("cer") is not None]
    latencies = [float(row["elapsed_sec"]) for row in rows if row.get("elapsed_sec") is not None]
    breakdown_total = Counter()
    by_length: dict[str, list[dict[str, Any]]] = defaultdict(list)
    digit_rows: list[dict[str, Any]] = []

    for row in scored:
        pred = row.get("prediction", {}).get("full_ocr_text", "")
        gold = row.get("gold_text", "")
        breakdown_total.update(char_error_breakdown(pred, gold))
        by_length[length_bin(gold)].append(row)
        if has_digit(gold):
            digit_rows.append(row)

    return {
        "summary": word_ocr_summary(rows),
        "latency": {
            "mean_sec": mean(latencies) if latencies else None,
            "p50_sec": median(latencies) if latencies else None,
            "p95_sec": percentile(latencies, 0.95),
            "p99_sec": percentile(latencies, 0.99),
            "max_sec": max(latencies) if latencies else None,
            "slow_threshold_sec": slow_threshold_sec,
            "slow_count": sum(1 for value in latencies if value >= slow_threshold_sec),
        },
        "timeouts": {
            "count": sum(1 for row in rows if "timeout" in str(row.get("error", "")).lower()),
            "image_ids": [
                row.get("image_id")
                for row in rows
                if "timeout" in str(row.get("error", "")).lower()
            ][:20],
        },
        "char_errors": dict(breakdown_total),
        "length_bins": {
            key: word_ocr_summary(value)
            for key, value in sorted(by_length.items())
        },
        "digit": {
            "n_records": len(digit_rows),
            "digit_exact_rate": (
                sum(
                    1
                    for row in digit_rows
                    if digits_only(row.get("prediction", {}).get("full_ocr_text")) == digits_only(row.get("gold_text"))
                )
                / len(digit_rows)
                if digit_rows
                else None
            ),
        },
        "worst_cer_examples": sorted(
            [
                {
                    "image_id": row.get("image_id"),
                    "cer": row.get("cer"),
                    "gold_text": snippet(row.get("gold_text")),
                    "prediction_text": snippet(row.get("prediction", {}).get("full_ocr_text")),
                }
                for row in scored
            ],
            key=lambda item: float(item["cer"] or 0),
            reverse=True,
        )[:10],
        "slow_examples": sorted(
            [
                {
                    "image_id": row.get("image_id"),
                    "elapsed_sec": row.get("elapsed_sec"),
                    "error": row.get("error"),
                    "cer": row.get("cer"),
                }
                for row in rows
                if row.get("elapsed_sec") is not None
            ],
            key=lambda item: float(item["elapsed_sec"] or 0),
            reverse=True,
        )[:10],
    }


def snippet(text: str | None, limit: int = 180) -> str:
    text = "" if text is None else str(text).replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "..."
