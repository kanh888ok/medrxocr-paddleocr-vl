#!/usr/bin/env python3
"""Check the real-shot mapping and manual QC tables.

This script verifies the first real-shot subset without running OCR inference.
It is meant to make the 20 / 18 / 2 counts reproducible:

- 20 real-shot images are listed.
- 18 images are eligible for strict eval.
- 2 images are collection examples because their original samples are train.
- every strict-eval row has clarity_check=pass and match_check=pass.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", default="docs/realshot_20_mapping.csv")
    parser.add_argument("--qc", default="docs/realshot_manual_qc.csv")
    parser.add_argument("--image-root", default="data/eval/realshot_images")
    parser.add_argument("--output", default="outputs/realshot_qc_check.json")
    parser.add_argument("--skip-image-check", action="store_true")
    args = parser.parse_args()

    mapping_path = Path(args.mapping)
    qc_path = Path(args.qc)
    image_root = Path(args.image_root)

    mapping_rows = read_csv(mapping_path)
    qc_rows = read_csv(qc_path)

    errors: list[str] = []
    if len(mapping_rows) != 20:
        errors.append(f"mapping row count is {len(mapping_rows)}, expected 20")
    if len(qc_rows) != 20:
        errors.append(f"QC row count is {len(qc_rows)}, expected 20")

    mapping_by_index = {row["real_index"]: row for row in mapping_rows}
    qc_by_index = {row["real_index"]: row for row in qc_rows}
    if set(mapping_by_index) != set(qc_by_index):
        errors.append("mapping and QC real_index sets do not match")

    split_counter = Counter(row.get("fixed_split", "missing") for row in qc_rows)
    qc_counter = Counter(row.get("qc_result", "missing") for row in qc_rows)
    strict_eval_rows = [row for row in qc_rows if row.get("evaluable_for_strict_eval") == "yes"]
    example_rows = [row for row in qc_rows if row.get("qc_result") == "collection_sample_only"]

    for row in qc_rows:
        idx = row["real_index"]
        mapping = mapping_by_index.get(idx)
        if not mapping:
            continue
        if row["original_image_id"] != mapping["dataset_image_id"]:
            errors.append(f"row {idx}: original_image_id does not match mapping")
        if row["fixed_split"] != mapping["fixed_split"]:
            errors.append(f"row {idx}: fixed_split does not match mapping")
        if row["clarity_check"] != "pass":
            errors.append(f"row {idx}: clarity_check is not pass")
        if row["match_check"] != "pass":
            errors.append(f"row {idx}: match_check is not pass")
        if row["evaluable_for_strict_eval"] == "yes" and row["fixed_split"] != "eval":
            errors.append(f"row {idx}: strict eval row is not from eval split")
        if row["fixed_split"] != "eval" and row["evaluable_for_strict_eval"] == "yes":
            errors.append(f"row {idx}: non-eval row marked evaluable")

    if len(strict_eval_rows) != 18:
        errors.append(f"strict eval count is {len(strict_eval_rows)}, expected 18")
    if len(example_rows) != 2:
        errors.append(f"collection sample count is {len(example_rows)}, expected 2")

    missing_images: list[str] = []
    if not args.skip_image_check:
        for row in qc_rows:
            image_path = image_root / row["realshot_file"]
            if not image_path.exists():
                missing_images.append(str(image_path))
        if missing_images:
            errors.append(f"{len(missing_images)} real-shot image files are missing under {image_root}")

    summary = {
        "mapping": str(mapping_path),
        "qc": str(qc_path),
        "n_mapping_rows": len(mapping_rows),
        "n_qc_rows": len(qc_rows),
        "split_counts": dict(split_counter),
        "qc_result_counts": dict(qc_counter),
        "strict_eval_count": len(strict_eval_rows),
        "collection_sample_count": len(example_rows),
        "missing_image_count": len(missing_images),
        "missing_image_examples": missing_images[:5],
        "passed": not errors,
        "errors": errors,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
