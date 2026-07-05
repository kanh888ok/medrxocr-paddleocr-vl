#!/usr/bin/env python3
"""Summarize word OCR predictions at fixed eval cutoffs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def summarize(rows: list[dict[str, Any]], n: int) -> dict[str, Any]:
    part = rows[:n]
    if not part:
        raise ValueError(f"empty prediction slice for n={n}")
    total_dist = sum(int(row["edit_distance"]) for row in part)
    total_chars = sum(int(row["gold_chars"]) for row in part)
    return {
        "n_completed": len(part),
        "errors": sum(1 for row in part if row.get("error")),
        "exact_match_rate": sum(1 for row in part if row.get("exact_match")) / len(part),
        "mean_cer": sum(float(row["cer"]) for row in part) / len(part),
        "micro_cer": total_dist / total_chars if total_chars else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--lora", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cutoffs", nargs="+", type=int, default=[100, 300, 400, 500])
    args = parser.parse_args()

    baseline = load_jsonl(Path(args.baseline))
    lora = load_jsonl(Path(args.lora))
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

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
