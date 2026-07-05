#!/usr/bin/env python3
"""Summarize word OCR predictions at fixed eval cutoffs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.data.loader import load_jsonl, write_json
from medrxocr.evaluation.metrics import word_ocr_summary


def summarize(rows: list[dict], n: int) -> dict:
    part = rows[:n]
    if not part:
        raise ValueError(f"empty prediction slice for n={n}")
    summary = word_ocr_summary(part)
    return {
        "n_completed": summary["n_scored"],
        "errors": summary["errors"],
        "exact_match_rate": summary["exact_match_rate"],
        "mean_cer": summary["mean_cer"],
        "micro_cer": summary["micro_cer"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--lora", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cutoffs", nargs="+", type=int, default=[100, 300, 400, 500])
    args = parser.parse_args()

    baseline = load_jsonl(args.baseline)
    lora = load_jsonl(args.lora)
    rows = []
    for n in args.cutoffs:
        if n > len(baseline) or n > len(lora):
            continue
        base_metrics = summarize(baseline, n)
        lora_metrics = summarize(lora, n)
        rows.append(
            {
                "n_images": n,
                "baseline": base_metrics,
                "lora": lora_metrics,
                "delta": {
                    "exact_match_rate": lora_metrics["exact_match_rate"] - base_metrics["exact_match_rate"],
                    "mean_cer": lora_metrics["mean_cer"] - base_metrics["mean_cer"],
                    "micro_cer": lora_metrics["micro_cer"] - base_metrics["micro_cer"],
                },
            }
        )

    result = {
        "task": "RxHandBD word OCR",
        "model_baseline": "PaddleOCR-VL-v1-local-max32",
        "model_lora": "MedRxOCR-LoRA-full-lr2e5-step512-max32",
        "eval_subset": "fixed leading slices from RxHandBD eval",
        "max_new_tokens": 32,
        "comparison": rows,
        "notes": [
            "Lower CER is better.",
            "This is a public word-crop OCR evaluation, not full prescription structured extraction.",
        ],
    }

    write_json(args.output, result)
    print(Path(args.output).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
