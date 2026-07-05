#!/usr/bin/env python3
"""Build a fixed public-data subset for the local LoRA/SFT run."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image

from build_erniekit_vl_sft_manifest import row_to_erniekit


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def image_area(row: dict[str, Any], root: Path) -> int:
    image_path = root / str(row["image_path"]).replace("\\", "/")
    with Image.open(image_path) as image:
        width, height = image.size
    return width * height


def group_key(row: dict[str, Any], root: Path, mendeley_max_chars: int, mendeley_max_area: int) -> str | None:
    metadata = row.get("metadata", {})
    source_id = metadata.get("source_id")
    task_type = metadata.get("task_type")
    if source_id == "mendeley_bilingual_1000":
        full_text = str(row.get("annotation", {}).get("full_ocr_text", ""))
        if len(full_text) > mendeley_max_chars:
            return None
        if image_area(row, root) > mendeley_max_area:
            return None
        return "mendeley_full_prescription"
    if source_id == "rxhandbd_5578" and task_type == "word_ocr":
        return "rxhandbd_word_ocr"
    return None


def stable_pick(
    rows: list[dict[str, Any]],
    root: Path,
    limits: dict[str, int],
    mendeley_max_chars: int,
    mendeley_max_area: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for row in sorted(rows, key=lambda item: str(item.get("image_id", ""))):
        key = group_key(row, root, mendeley_max_chars, mendeley_max_area)
        if key is None or counts[key] >= limits.get(key, 0):
            continue
        selected.append(row)
        counts[key] += 1
    missing = {key: limit - counts[key] for key, limit in limits.items() if counts[key] < limit}
    if missing:
        raise RuntimeError(f"Not enough records for requested limits: {missing}")
    return selected


def task_for_row(row: dict[str, Any], mendeley_task: str, rxhandbd_task: str) -> str:
    metadata = row.get("metadata", {})
    if metadata.get("source_id") == "mendeley_bilingual_1000":
        return mendeley_task
    if metadata.get("source_id") == "rxhandbd_5578":
        return rxhandbd_task
    return "auto"


def write_erniekit(rows: list[dict[str, Any]], path: Path, root: Path, mendeley_task: str, rxhandbd_task: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            task = task_for_row(row, mendeley_task, rxhandbd_task)
            f.write(json.dumps(row_to_erniekit(row, str(root), task), ensure_ascii=False) + "\n")


def summarize(rows: list[dict[str, Any]], root: Path, mendeley_max_chars: int, mendeley_max_area: int) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    char_lengths: list[int] = []
    image_areas: list[int] = []
    for row in rows:
        key = group_key(row, root, mendeley_max_chars, mendeley_max_area) or "other"
        counts[key] += 1
        char_lengths.append(len(str(row.get("annotation", {}).get("full_ocr_text", ""))))
        image_areas.append(image_area(row, root))
    return {
        "records": len(rows),
        "groups": dict(counts),
        "min_full_ocr_chars": min(char_lengths) if char_lengths else 0,
        "max_full_ocr_chars": max(char_lengths) if char_lengths else 0,
        "mean_full_ocr_chars": round(sum(char_lengths) / len(char_lengths), 2) if char_lengths else 0,
        "max_image_area": max(image_areas) if image_areas else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--train-input", default="data/processed/medrxocr_train.jsonl")
    parser.add_argument("--val-input", default="data/processed/medrxocr_val.jsonl")
    parser.add_argument("--train-output", default="data/processed/train_rx_erniekit_sft_public_small512.jsonl")
    parser.add_argument("--val-output", default="data/processed/val_rx_erniekit_sft_public_small100.jsonl")
    parser.add_argument("--summary-output", default="outputs/lora_public_small_subset_summary.json")
    parser.add_argument("--mendeley-train", type=int, default=180)
    parser.add_argument("--rxhandbd-train", type=int, default=332)
    parser.add_argument("--mendeley-val", type=int, default=30)
    parser.add_argument("--rxhandbd-val", type=int, default=70)
    parser.add_argument("--mendeley-max-chars", type=int, default=500)
    parser.add_argument("--mendeley-max-area", type=int, default=1300000)
    parser.add_argument("--mendeley-task", choices=["ocr", "full_json"], default="ocr")
    parser.add_argument("--rxhandbd-task", choices=["ocr", "word_ocr"], default="word_ocr")
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    train_rows = stable_pick(
        load_jsonl(repo_root / args.train_input),
        repo_root,
        {"mendeley_full_prescription": args.mendeley_train, "rxhandbd_word_ocr": args.rxhandbd_train},
        args.mendeley_max_chars,
        args.mendeley_max_area,
    )
    val_rows = stable_pick(
        load_jsonl(repo_root / args.val_input),
        repo_root,
        {"mendeley_full_prescription": args.mendeley_val, "rxhandbd_word_ocr": args.rxhandbd_val},
        args.mendeley_max_chars,
        args.mendeley_max_area,
    )

    write_erniekit(train_rows, repo_root / args.train_output, repo_root, args.mendeley_task, args.rxhandbd_task)
    write_erniekit(val_rows, repo_root / args.val_output, repo_root, args.mendeley_task, args.rxhandbd_task)

    summary = {
        "name": "lora_public_small",
        "train": summarize(train_rows, repo_root, args.mendeley_max_chars, args.mendeley_max_area),
        "val": summarize(val_rows, repo_root, args.mendeley_max_chars, args.mendeley_max_area),
        "source_note": "Public de-identified data only; no private offline prescriptions.",
        "selection": "Deterministic by image_id within fixed train/val splits.",
        "mendeley_max_chars": args.mendeley_max_chars,
        "mendeley_max_area": args.mendeley_max_area,
        "mendeley_task": args.mendeley_task,
        "rxhandbd_task": args.rxhandbd_task,
        "outputs": {
            "train": args.train_output,
            "val": args.val_output,
        },
    }
    summary_path = repo_root / args.summary_output
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
