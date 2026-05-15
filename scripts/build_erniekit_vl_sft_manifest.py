#!/usr/bin/env python3
"""Build ERNIEKit PaddleOCR-VL SFT JSONL from MedRxOCR annotations.

Official PaddleOCR-VL SFT uses records with `image_info` and `text_info`.
Each sample alternates a masked prompt and an unmasked target answer:

{
  "image_info": [{"matched_text_index": 0, "image_url": "..."}],
  "text_info": [
    {"text": "OCR:", "tag": "mask"},
    {"text": "recognized text", "tag": "no_mask"}
  ]
}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROMPTS = {
    "full_json": "Extract this medical prescription as valid MedRxOCR JSON. Output JSON only.",
    "ocr": "OCR:",
    "word_ocr": "Recognize the handwritten prescription word. Output text only.",
    "region": "Detect medicine-name regions and output bounding boxes in JSON.",
}


def target_for_row(row: dict[str, Any], task: str) -> tuple[str, str]:
    ann = row.get("annotation", {})
    metadata = row.get("metadata", {})
    task_type = metadata.get("task_type")

    if task == "auto":
        if task_type == "word_ocr":
            task = "word_ocr"
        elif task_type == "medicine_region_detection":
            task = "region"
        else:
            task = "full_json"

    if task == "word_ocr":
        return PROMPTS["word_ocr"], str(ann.get("full_ocr_text", ""))
    if task == "ocr":
        return PROMPTS["ocr"], str(ann.get("full_ocr_text", ""))
    if task == "region":
        return PROMPTS["region"], json.dumps({"regions": ann.get("regions", [])}, ensure_ascii=False)
    if task == "full_json":
        return PROMPTS["full_json"], json.dumps(ann, ensure_ascii=False, separators=(",", ":"))
    raise ValueError(f"Unsupported task: {task}")


def row_to_erniekit(row: dict[str, Any], root: str, task: str) -> dict[str, Any]:
    prompt, answer = target_for_row(row, task)
    image_path = str(row["image_path"]).replace("\\", "/")
    if root:
        image_path = str(Path(root) / image_path).replace("\\", "/")
    return {
        "image_info": [{"matched_text_index": 0, "image_url": image_path}],
        "text_info": [
            {"text": prompt, "tag": "mask"},
            {"text": answer, "tag": "no_mask"},
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="MedRxOCR JSONL file")
    parser.add_argument("--output", required=True, help="ERNIEKit SFT JSONL output")
    parser.add_argument("--root", default="", help="Optional image path prefix for training host")
    parser.add_argument(
        "--task",
        default="auto",
        choices=["auto", "full_json", "ocr", "word_ocr", "region"],
        help="Target task. auto uses each row's metadata.task_type when available.",
    )
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with inp.open("r", encoding="utf-8") as f, out.open("w", encoding="utf-8") as g:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            g.write(json.dumps(row_to_erniekit(row, args.root, args.task), ensure_ascii=False) + "\n")
            n += 1

    print(f"Wrote {n} ERNIEKit PaddleOCR-VL SFT records to {out}")


if __name__ == "__main__":
    main()
