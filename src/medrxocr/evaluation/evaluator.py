"""Reusable evaluators."""

from __future__ import annotations

from typing import Any

from .metrics import char_error_breakdown, exact_match, text_cer, word_ocr_summary
from medrxocr.utils.text import normalize_text


class WordOcrEvaluator:
    """Evaluate OCR text predictions against gold text."""

    def evaluate_pair(self, prediction: str | None, gold: str | None) -> dict[str, Any]:
        breakdown = char_error_breakdown(prediction, gold)
        truth = normalize_text(gold)
        return {
            "normalized_gold": truth,
            "normalized_prediction": normalize_text(prediction),
            "exact_match": exact_match(prediction, gold),
            "edit_distance": breakdown["edit_distance"],
            "gold_chars": max(len(truth), 1),
            "cer": text_cer(prediction, gold),
            "error_breakdown": breakdown,
        }

    def summarize(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        return word_ocr_summary(rows)
