#!/usr/bin/env python3
"""Quality audit for MedRxOCR JSONL."""

import argparse, json, hashlib
from pathlib import Path
from collections import Counter

REQUIRED = ["image_id", "image_path", "split", "metadata", "annotation"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--annotations", required=True)
    p.add_argument("--root", default=".")
    p.add_argument("--output", default=None)
    args = p.parse_args()

    root = Path(args.root)
    seen = set()
    duplicate_ids = []
    missing_files = []
    pii_bad = []
    missing_required = []
    tag_counter = Counter()
    difficulty_counter = Counter()
    source_counter = Counter()
    n = 0

    with Path(args.annotations).open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip(): continue
            n += 1
            row = json.loads(line)
            for k in REQUIRED:
                if k not in row:
                    missing_required.append([i, k])
            image_id = row.get("image_id")
            if image_id in seen:
                duplicate_ids.append(image_id)
            seen.add(image_id)

            imgp = row.get("image_path", "")
            if imgp and not (root / imgp).exists() and not Path(imgp).exists():
                missing_files.append(imgp)

            meta = row.get("metadata", {})
            if meta.get("pii_redacted") is not True:
                pii_bad.append(image_id)
            for t in meta.get("visual_tags", []):
                tag_counter[t] += 1
            difficulty_counter[meta.get("difficulty", "missing")] += 1
            source_counter[meta.get("source_id", "missing")] += 1

    report = {
        "n_records": n,
        "n_duplicate_ids": len(duplicate_ids),
        "duplicate_ids_examples": duplicate_ids[:20],
        "n_missing_files": len(missing_files),
        "missing_files_examples": missing_files[:20],
        "n_pii_not_redacted": len(pii_bad),
        "pii_not_redacted_examples": pii_bad[:20],
        "n_missing_required": len(missing_required),
        "missing_required_examples": missing_required[:20],
        "visual_tags": dict(tag_counter),
        "difficulty": dict(difficulty_counter),
        "sources": dict(source_counter)
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()
