#!/usr/bin/env python3
"""Build a hard-sample word-OCR SFT manifest from the training split."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.data.loader import filter_records, load_jsonl, write_json
from medrxocr.training.selection import hard_sample_features, hard_sample_score, prediction_by_image_id, select_hard_samples

from build_erniekit_vl_sft_manifest import row_to_erniekit


def load_predictions(path: Path | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    return prediction_by_image_id(load_jsonl(path))


def write_manifest(rows: list[dict[str, Any]], output: Path, root: Path, task: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row_to_erniekit(row, str(root), task), ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="data/processed/medrxocr_train.jsonl")
    parser.add_argument("--output", default="data/processed/train_rx_erniekit_sft_word_hard512.jsonl")
    parser.add_argument("--summary-output", default="outputs/lora_hard_word_manifest_summary.json")
    parser.add_argument("--predictions", default=None, help="Optional predictions on the training split, not eval.")
    parser.add_argument("--source-id", default="rxhandbd_5578")
    parser.add_argument("--task-type", default="word_ocr")
    parser.add_argument("--task", choices=["ocr", "word_ocr"], default="ocr")
    parser.add_argument("--limit", type=int, default=512)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    predictions = load_predictions(root / args.predictions if args.predictions else None)
    rows = filter_records(load_jsonl(root / args.input), args.source_id, args.task_type)
    selected = select_hard_samples(rows, args.limit, predictions)

    write_manifest(selected, root / args.output, root, args.task)
    preview = []
    for row in selected[:20]:
        pred = predictions.get(str(row.get("image_id")))
        preview.append(
            {
                "image_id": row.get("image_id"),
                "score": hard_sample_score(row, pred),
                "features": hard_sample_features(row, pred),
            }
        )
    summary = {
        "input": args.input,
        "output": args.output,
        "source_id": args.source_id,
        "task_type": args.task_type,
        "task_prompt": args.task,
        "available_records": len(rows),
        "selected_records": len(selected),
        "selection": "Training split only. Uses label length/digits/difficulty, plus optional train-set CER if provided.",
        "used_prediction_file": args.predictions,
        "preview": preview,
    }
    write_json(root / args.summary_output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
