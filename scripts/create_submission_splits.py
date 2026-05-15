#!/usr/bin/env python3
"""Create fixed MedRxOCR train/val/eval JSONL files.

The script is deterministic: splits are assigned from a stable SHA256 hash of
source_id + image_id, so the same inputs always produce the same outputs.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def bucket(row):
    key = f"{row.get('metadata', {}).get('source_id', '')}:{row['image_id']}"
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16) % 100


def set_split(row, split):
    row = dict(row)
    row["split"] = split
    return row


def read_jsonl(path):
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def split_unassigned(row):
    b = bucket(row)
    if b < 70:
        return "train"
    if b < 80:
        return "val"
    return "eval"


def split_official_train(row):
    return "val" if bucket(row) < 10 else "train"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mendeley", required=True)
    p.add_argument("--rxhandbd-train", required=True)
    p.add_argument("--rxhandbd-eval", required=True)
    p.add_argument("--bd200", required=True)
    p.add_argument("--output-dir", default="data/processed")
    args = p.parse_args()

    rows = []

    for row in read_jsonl(args.mendeley):
        rows.append(set_split(row, split_unassigned(row)))

    for row in read_jsonl(args.bd200):
        rows.append(set_split(row, split_unassigned(row)))

    for row in read_jsonl(args.rxhandbd_train):
        rows.append(set_split(row, split_official_train(row)))

    for row in read_jsonl(args.rxhandbd_eval):
        rows.append(set_split(row, "eval"))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "train": out_dir / "medrxocr_train.jsonl",
        "val": out_dir / "medrxocr_val.jsonl",
        "eval": out_dir / "medrxocr_eval.jsonl",
    }

    counters = Counter()
    handles = {k: v.open("w", encoding="utf-8") for k, v in outputs.items()}
    try:
        for row in rows:
            split = row["split"]
            handles[split].write(json.dumps(row, ensure_ascii=False) + "\n")
            counters[(split, row.get("metadata", {}).get("source_id", "missing"))] += 1
    finally:
        for h in handles.values():
            h.close()

    summary = {
        split: {
            source: count
            for (split_name, source), count in sorted(counters.items())
            if split_name == split
        }
        for split in ["train", "val", "eval"]
    }
    summary["total"] = sum(counters.values())
    summary_path = out_dir / "split_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
