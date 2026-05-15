#!/usr/bin/env python3
"""Generate MedRxOCR dataset statistics."""

import argparse, json
from pathlib import Path
from collections import Counter

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--annotations", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    counters = {
        "split": Counter(),
        "source_id": Counter(),
        "difficulty": Counter(),
        "language": Counter(),
        "visual_tags": Counter(),
        "task_type": Counter(),
    }
    n = 0
    n_meds = 0
    n_regions = 0
    text_lens = []

    with Path(args.annotations).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            row = json.loads(line)
            n += 1
            meta = row.get("metadata", {})
            ann = row.get("annotation", {})
            counters["split"][row.get("split", "missing")] += 1
            counters["source_id"][meta.get("source_id", "missing")] += 1
            counters["difficulty"][meta.get("difficulty", "missing")] += 1
            counters["task_type"][meta.get("task_type", "full_page")] += 1
            for lang in meta.get("language", []):
                counters["language"][lang] += 1
            for tag in meta.get("visual_tags", []):
                counters["visual_tags"][tag] += 1
            meds = ann.get("medications", [])
            regs = ann.get("regions", [])
            n_meds += len(meds) if isinstance(meds, list) else 0
            n_regions += len(regs) if isinstance(regs, list) else 0
            text_lens.append(len(ann.get("full_ocr_text", "")))

    stats = {k: dict(v) for k, v in counters.items()}
    stats.update({
        "n_records": n,
        "n_medication_lines": n_meds,
        "n_regions": n_regions,
        "avg_full_ocr_text_len": sum(text_lens) / len(text_lens) if text_lens else 0,
        "max_full_ocr_text_len": max(text_lens) if text_lens else 0
    })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
