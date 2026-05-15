#!/usr/bin/env python3
"""Convert RxHandBD labels into MedRxOCR word-recognition JSONL.

Example:
python scripts/prepare_rxhandbd.py \
  --labels data/raw/rxhandbd/train_labels.csv \
  --image-root data/raw/rxhandbd/train \
  --split train \
  --output data/interim/rxhandbd_train.jsonl
"""

import argparse
import csv
import json
from pathlib import Path


def find_col(fieldnames, candidates):
    lowered = {c.lower().strip(): c for c in fieldnames}
    for cand in candidates:
        for lc, orig in lowered.items():
            if cand in lc:
                return orig
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", required=True)
    p.add_argument("--image-root", required=True)
    p.add_argument("--split", required=True, choices=["train", "val", "eval", "test"])
    p.add_argument("--output", required=True)
    p.add_argument("--source-id", default="rxhandbd_5578")
    p.add_argument("--license", default="CC BY 4.0")
    args = p.parse_args()

    labels = Path(args.labels)
    image_root = Path(args.image_root)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    with labels.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        img_col = find_col(fields, ["image", "file", "filename", "img", "path"])
        label_col = find_col(fields, ["label", "text", "word", "transcription"])
        if img_col is None or label_col is None:
            raise SystemExit(f"Could not infer image/label columns from: {fields}")

        n = 0
        with out.open("w", encoding="utf-8") as g:
            for row in reader:
                img = row.get(img_col, "").strip()
                label = row.get(label_col, "").strip()
                if not img:
                    continue
                image_id = Path(img).stem
                rec = {
                    "image_id": f"rxhandbd_{args.split}_{image_id}",
                    "image_path": (image_root / img).as_posix(),
                    "split": args.split,
                    "metadata": {
                        "source_id": args.source_id,
                        "license": args.license,
                        "source_type": "public_deidentified_cropped_prescription_word",
                        "pii_redacted": True,
                        "language": ["en", "bn"],
                        "visual_tags": ["handwritten", "cropped_word"],
                        "difficulty": "medium",
                        "task_type": "word_ocr"
                    },
                    "annotation": {
                        "document_type": "prescription_word",
                        "patient": {"name": None, "age": None, "sex": None, "patient_id": None},
                        "visit": {"date": None, "department": None, "diagnosis": None},
                        "medications": [],
                        "doctor": {"name": None, "signature_present": False, "stamp_present": False},
                        "regions": [],
                        "full_ocr_text": label
                    }
                }
                g.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1

    print(f"Wrote {n} records to {out}")


if __name__ == "__main__":
    main()
