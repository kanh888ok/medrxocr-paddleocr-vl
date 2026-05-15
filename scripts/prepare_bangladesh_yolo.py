#!/usr/bin/env python3
"""Convert YOLO medicine-name boxes to MedRxOCR region annotations.

Expected:
- image-root contains images.
- label-root contains .txt files with YOLO format: class x_center y_center width height
- class label defaults to medicine_region.

Example:
python scripts/prepare_bangladesh_yolo.py \
  --image-root data/raw/bd200/images \
  --label-root data/raw/bd200/labels \
  --output data/interim/bd200_regions.jsonl
"""

import argparse
import json
from pathlib import Path
from PIL import Image


def yolo_to_xyxy(xc, yc, w, h, W, H):
    x1 = (xc - w / 2) * W
    y1 = (yc - h / 2) * H
    x2 = (xc + w / 2) * W
    y2 = (yc + h / 2) * H
    return [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image-root", required=True)
    p.add_argument("--label-root", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--source-id", default="mendeley_bd_200_yolo")
    p.add_argument("--license", default="CC BY 4.0")
    args = p.parse_args()

    image_root = Path(args.image_root)
    label_root = Path(args.label_root)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = sorted([p for p in image_root.rglob("*") if p.suffix.lower() in image_exts])

    n = 0
    with out.open("w", encoding="utf-8") as g:
        for img_path in images:
            label_path = label_root / (img_path.stem + ".txt")
            regions = []
            try:
                with Image.open(img_path) as im:
                    W, H = im.size
            except Exception:
                W, H = 1, 1

            if label_path.exists():
                for line in label_path.read_text(encoding="utf-8").splitlines():
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    _, xc, yc, w, h = parts
                    bbox = yolo_to_xyxy(float(xc), float(yc), float(w), float(h), W, H)
                    regions.append({"label": "medicine_region", "bbox": bbox, "text": None})

            rec = {
                "image_id": f"bd200_{img_path.stem}",
                "image_path": img_path.as_posix(),
                "split": "unassigned",
                "metadata": {
                    "source_id": args.source_id,
                    "license": args.license,
                    "source_type": "public_deidentified_prescription_yolo_regions",
                    "pii_redacted": True,
                    "language": ["bn", "en"],
                    "visual_tags": ["handwritten", "printed", "mixed_language"],
                    "difficulty": "medium",
                    "task_type": "medicine_region_detection"
                },
                "annotation": {
                    "document_type": "prescription",
                    "patient": {"name": "[REDACTED]", "age": None, "sex": None, "patient_id": "[REDACTED]"},
                    "visit": {"date": None, "department": None, "diagnosis": None},
                    "medications": [],
                    "doctor": {"name": "[REDACTED]", "signature_present": False, "stamp_present": False},
                    "regions": regions,
                    "full_ocr_text": ""
                }
            }
            g.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1

    print(f"Wrote {n} records to {out}")


if __name__ == "__main__":
    main()
