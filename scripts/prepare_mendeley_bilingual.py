#!/usr/bin/env python3
"""Convert Mendeley bilingual prescription annotations into MedRxOCR JSONL.

Expected CSV:
- The script is robust to different column names.
- It searches for image filename and Bangla/English text columns.

Example:
python scripts/prepare_mendeley_bilingual.py \
  --csv data/raw/mendeley_bilingual/annotations.csv \
  --image-root data/raw/mendeley_bilingual/images \
  --output data/interim/mendeley_bilingual.jsonl
"""

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


def find_col(fieldnames, candidates):
    lowered = {c.lower().strip(): c for c in fieldnames}
    for cand in candidates:
        for lc, orig in lowered.items():
            if cand in lc:
                return orig
    return None


def infer_difficulty(text: str) -> str:
    n = len(text.strip())
    if n == 0:
        return "hard"
    if n < 80:
        return "easy"
    if n < 250:
        return "medium"
    return "hard"


def build_annotation(text: str, lang_tags):
    return {
        "document_type": "prescription",
        "patient": {
            "name": "[REDACTED]",
            "age": None,
            "sex": None,
            "patient_id": "[REDACTED]"
        },
        "visit": {
            "date": None,
            "department": None,
            "diagnosis": None
        },
        "medications": [],
        "doctor": {
            "name": "[REDACTED]",
            "signature_present": False,
            "stamp_present": False
        },
        "regions": [],
        "full_ocr_text": text
    }


def build_image_index(image_root: Path):
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    by_name = {}
    by_stem = {}
    for path in image_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in image_exts:
            continue
        rel = path.relative_to(image_root)
        by_name[path.name.lower()] = rel
        by_stem.setdefault(path.stem.lower(), rel)
    return by_name, by_stem


def normalize_image_name(name: str) -> str:
    name = name.strip().replace("\\", "/").split("/")[-1]
    for bad, good in {
        ",jpg": ".jpg",
        ",jpeg": ".jpeg",
        ",png": ".png",
    }.items():
        if name.lower().endswith(bad):
            return name[: -len(bad)] + good
    return name


def resolve_image_path(image_root: Path, img_name: str, by_name, by_stem) -> str:
    normalized = normalize_image_name(img_name)
    rel = by_name.get(normalized.lower())
    if rel is None:
        rel = by_stem.get(Path(normalized).stem.lower())
    return (image_root / (rel if rel is not None else normalized)).as_posix()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--image-root", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--source-id", default="mendeley_bilingual_1000")
    p.add_argument("--license", default="CC BY 4.0")
    args = p.parse_args()

    csv_path = Path(args.csv)
    image_root = Path(args.image_root)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    by_name, by_stem = build_image_index(image_root)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        img_col = find_col(fields, ["image", "file", "filename", "img"])
        en_col = find_col(fields, ["english", "eng", "en_text"])
        bn_col = find_col(fields, ["bangla", "bengali", "bn", "bangla_text"])
        id_col = find_col(fields, ["id", "number", "index"])

        if img_col is None:
            raise SystemExit(f"Could not infer image filename column from: {fields}")

        n = 0
        skipped_duplicates = 0
        seen_ids = set()
        with out.open("w", encoding="utf-8") as g:
            for row in reader:
                img_name = row.get(img_col, "").strip()
                if not img_name:
                    continue
                image_path = resolve_image_path(image_root, img_name, by_name, by_stem)

                texts = []
                lang = []
                if en_col and row.get(en_col, "").strip():
                    texts.append(row[en_col].strip())
                    lang.append("en")
                if bn_col and row.get(bn_col, "").strip():
                    texts.append(row[bn_col].strip())
                    lang.append("bn")

                text = "\n".join(texts).strip()
                if not lang:
                    lang = ["unknown"]

                image_id_raw = row.get(id_col, "").strip() if id_col else ""
                image_id = image_id_raw or Path(img_name).stem
                image_id = re.sub(r"[^A-Za-z0-9_\-]+", "_", image_id)
                if image_id in seen_ids:
                    skipped_duplicates += 1
                    continue
                seen_ids.add(image_id)

                rec = {
                    "image_id": f"rx_{args.source_id}_{image_id}",
                    "image_path": image_path,
                    "split": "unassigned",
                    "metadata": {
                        "source_id": args.source_id,
                        "license": args.license,
                        "source_type": "public_deidentified_prescription_dataset",
                        "pii_redacted": True,
                        "language": lang,
                        "visual_tags": ["handwritten", "mixed_language"] if len(lang) > 1 else ["handwritten"],
                        "difficulty": infer_difficulty(text)
                    },
                    "annotation": build_annotation(text, lang)
                }
                g.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1

    print(f"Wrote {n} records to {out}")
    if skipped_duplicates:
        print(f"Skipped {skipped_duplicates} duplicate image_id rows")


if __name__ == "__main__":
    main()
