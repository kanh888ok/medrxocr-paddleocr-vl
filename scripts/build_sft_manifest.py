#!/usr/bin/env python3
"""Build PaddleOCR-VL SFT JSONL from MedRxOCR annotations."""

import argparse, json
from pathlib import Path

PROMPTS = {
    "full_json": "<image>Extract this medical prescription as valid MedRxOCR JSON. Preserve raw text, use [UNK] for unreadable values, and output JSON only.",
    "ocr": "<image>OCR:",
    "word_ocr": "<image>Recognize the handwritten prescription word. Output text only.",
    "region": "<image>Detect medicine-name regions and output bounding boxes in JSON."
}

def record_to_sft(row, task="full_json"):
    ann = row["annotation"]
    if task == "ocr" or row.get("metadata", {}).get("task_type") == "word_ocr":
        output = ann.get("full_ocr_text", "")
        prompt = PROMPTS["word_ocr"] if row.get("metadata", {}).get("task_type") == "word_ocr" else PROMPTS["ocr"]
    elif row.get("metadata", {}).get("task_type") == "medicine_region_detection":
        output = json.dumps({"regions": ann.get("regions", [])}, ensure_ascii=False)
        prompt = PROMPTS["region"]
    else:
        output = json.dumps(ann, ensure_ascii=False)
        prompt = PROMPTS["full_json"]
    return {"messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": output}], "images": [row["image_path"]]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--task", default="auto", choices=["auto", "full_json", "ocr"])
    args = p.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with inp.open("r", encoding="utf-8") as f, out.open("w", encoding="utf-8") as g:
        for line in f:
            if not line.strip(): 
                continue
            row = json.loads(line)
            task = "full_json" if args.task == "auto" else args.task
            g.write(json.dumps(record_to_sft(row, task), ensure_ascii=False) + "\n")
            n += 1
    print(f"Wrote {n} SFT records to {out}")

if __name__ == "__main__":
    main()
