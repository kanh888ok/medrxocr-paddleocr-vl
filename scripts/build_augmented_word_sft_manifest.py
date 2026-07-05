#!/usr/bin/env python3
"""Build a camera-augmented RxHandBD word-OCR SFT manifest.

The script writes augmented images under data/interim by default. Those files
are intentionally not tracked in Git.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.data.augmentation import resolve_variants, save_augmented_image
from medrxocr.data.loader import filter_records, load_jsonl, write_json

from build_erniekit_vl_sft_manifest import row_to_erniekit


def augmented_row(row: dict[str, Any], image_path: str, variant_name: str) -> dict[str, Any]:
    new_row = copy.deepcopy(row)
    new_row["image_id"] = f"{row['image_id']}__aug_{variant_name}"
    new_row["image_path"] = image_path
    metadata = new_row.setdefault("metadata", {})
    metadata["augmentation"] = {
        "source_image_id": row["image_id"],
        "variant": variant_name,
    }
    return new_row


def write_manifest(rows: list[dict[str, Any]], output: Path, root: Path, task: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row_to_erniekit(row, str(root), task), ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="data/processed/medrxocr_train.jsonl")
    parser.add_argument("--output", default="data/processed/train_rx_erniekit_sft_word_aug_camera.jsonl")
    parser.add_argument("--image-output-dir", default="data/interim/rxhandbd_camera_aug")
    parser.add_argument("--summary-output", default="outputs/lora_augmented_word_manifest_summary.json")
    parser.add_argument("--source-id", default="rxhandbd_5578")
    parser.add_argument("--task-type", default="word_ocr")
    parser.add_argument("--task", choices=["ocr", "word_ocr"], default="ocr")
    parser.add_argument("--variants", nargs="*", default=["blur", "bright", "rotate", "perspective"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--augmentation-limit",
        type=int,
        default=None,
        help="Augment only the first N selected source records. Originals still use the full selected set.",
    )
    parser.add_argument("--include-original", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rows = filter_records(load_jsonl(root / args.input), args.source_id, args.task_type, args.limit)
    augment_rows = rows[: args.augmentation_limit] if args.augmentation_limit else rows
    variants = resolve_variants(args.variants)
    output_image_dir = root / args.image_output_dir

    manifest_rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    if args.include_original:
        manifest_rows.extend(rows)
        counts["original"] = len(rows)

    for row in augment_rows:
        src_path = root / str(row["image_path"]).replace("\\", "/")
        stem = Path(row["image_path"]).stem
        suffix = Path(row["image_path"]).suffix or ".jpg"
        for spec in variants:
            rel_path = Path(args.image_output_dir) / spec.name / f"{stem}__{spec.name}{suffix}"
            save_augmented_image(src_path, root / rel_path, spec)
            manifest_rows.append(augmented_row(row, str(rel_path).replace("\\", "/"), spec.name))
            counts[spec.name] += 1

    write_manifest(manifest_rows, root / args.output, root, args.task)
    summary = {
        "input": args.input,
        "output": args.output,
        "image_output_dir": args.image_output_dir,
        "source_id": args.source_id,
        "task_type": args.task_type,
        "task_prompt": args.task,
        "source_records": len(rows),
        "augmented_source_records": len(augment_rows),
        "manifest_records": len(manifest_rows),
        "variants": dict(counts),
        "note": "Generated images are ignored by Git. Rebuild them before running the augmented LoRA config.",
    }
    write_json(root / args.summary_output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
