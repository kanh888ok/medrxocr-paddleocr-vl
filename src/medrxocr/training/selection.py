"""Sample selection helpers for LoRA/SFT follow-up experiments."""

from __future__ import annotations

from typing import Any

from medrxocr.data.loader import annotation_text
from medrxocr.utils.text import has_digit


def prediction_by_image_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("image_id")): row for row in rows if row.get("image_id")}


def hard_sample_features(row: dict[str, Any], prediction: dict[str, Any] | None = None) -> dict[str, Any]:
    text = annotation_text(row)
    metadata = row.get("metadata", {})
    visual_tags = set(metadata.get("visual_tags", []))
    difficulty = str(metadata.get("difficulty", "")).lower()
    features = {
        "text_length": len(text),
        "has_digit": has_digit(text),
        "marked_hard": difficulty == "hard",
        "handwritten": "handwritten" in visual_tags,
        "prediction_cer": None,
        "prediction_error": False,
    }
    if prediction:
        features["prediction_cer"] = prediction.get("cer")
        features["prediction_error"] = bool(prediction.get("error"))
    return features


def hard_sample_score(row: dict[str, Any], prediction: dict[str, Any] | None = None) -> float:
    features = hard_sample_features(row, prediction)
    score = min(float(features["text_length"]) / 8.0, 2.0)
    if features["has_digit"]:
        score += 0.8
    if features["marked_hard"]:
        score += 0.8
    if features["handwritten"]:
        score += 0.4
    if features["prediction_cer"] is not None:
        score += min(float(features["prediction_cer"]) * 4.0, 4.0)
    if features["prediction_error"]:
        score += 1.0
    return round(score, 6)


def select_hard_samples(
    rows: list[dict[str, Any]],
    limit: int,
    predictions: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    predictions = predictions or {}
    scored = [
        (
            hard_sample_score(row, predictions.get(str(row.get("image_id")))),
            str(row.get("image_id", "")),
            row,
        )
        for row in rows
    ]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [row for _, _, row in scored[:limit]]
