#!/usr/bin/env python3
"""Run PaddleOCR-VL zero-shot evaluation on cropped word OCR records.

The intended first use is the full RxHandBD eval subset:

python scripts/run_paddleocrvl_word_eval.py \
  --root . \
  --input data/processed/medrxocr_eval.jsonl \
  --output-dir outputs/paddleocrvl_v15_rxhandbd_word_eval \
  --source-id rxhandbd_5578 \
  --task-type word_ocr \
  --pipeline-version v1.5 \
  --disable-layout
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


def norm_text(text: str | None) -> str:
    text = "" if text is None else str(text)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def edit_distance(a: str, b: str) -> tuple[int, int]:
    a = norm_text(a)
    b = norm_text(b)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1], max(len(b), 1)


def flatten_strings(obj: Any) -> list[str]:
    texts: list[str] = []
    if isinstance(obj, str):
        if obj.strip():
            texts.append(obj)
    elif isinstance(obj, dict):
        for key in ("block_content", "rec_text", "text", "label"):
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                texts.append(val)
        for val in obj.values():
            if isinstance(val, (dict, list)):
                texts.extend(flatten_strings(val))
    elif isinstance(obj, list):
        for item in obj:
            texts.extend(flatten_strings(item))
    return texts


def result_text(item: Any) -> str:
    markdown = getattr(item, "markdown", None)
    if isinstance(markdown, str) and markdown.strip():
        return markdown.strip()

    data = getattr(item, "json", None)
    if isinstance(data, dict):
        blocks = data.get("res", {}).get("parsing_res_list", [])
        block_text = "\n".join(
            str(block.get("block_content", "")).strip()
            for block in blocks
            if isinstance(block, dict) and str(block.get("block_content", "")).strip()
        )
        if block_text:
            return block_text
        texts = flatten_strings(data)
        if texts:
            return "\n".join(dict.fromkeys(texts))

    return str(item).strip()


def load_rows(path: Path, source_id: str | None, task_type: str | None, limit: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            metadata = row.get("metadata", {})
            if source_id and metadata.get("source_id") != source_id:
                continue
            if task_type and metadata.get("task_type") != task_type:
                continue
            rows.append(row)
            if limit and len(rows) >= limit:
                break
    return rows


def load_done_ids(path: Path) -> set[str]:
    done: set[str] = set()
    if not path.exists():
        return done
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("image_id"):
                done.add(row["image_id"])
    return done


def build_pipeline(args: argparse.Namespace) -> Any:
    from paddleocr import PaddleOCRVL

    kwargs: dict[str, Any] = {"pipeline_version": args.pipeline_version}
    if args.vl_rec_model_dir:
        kwargs["vl_rec_model_dir"] = args.vl_rec_model_dir
    if args.disable_layout:
        kwargs["use_layout_detection"] = False
    if args.cache_root:
        cache_root = Path(args.cache_root)
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(cache_root / "paddlex_cache"))
        os.environ.setdefault("HF_HOME", str(cache_root / "hf_cache"))
        os.environ.setdefault("MODELSCOPE_CACHE", str(cache_root / "modelscope_cache"))
    return PaddleOCRVL(**kwargs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="data/processed/medrxocr_eval.jsonl")
    parser.add_argument("--output-dir", default="outputs/paddleocrvl_v15_rxhandbd_word_eval")
    parser.add_argument("--source-id", default="rxhandbd_5578")
    parser.add_argument("--task-type", default="word_ocr")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--pipeline-version", default="v1.5")
    parser.add_argument("--vl-rec-model-dir", default=None)
    parser.add_argument("--model-label", default=None)
    parser.add_argument("--cache-root", default=None)
    parser.add_argument("--max-new-tokens", type=int, default=None)
    parser.add_argument("--disable-layout", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    input_path = Path(args.input)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "predictions.jsonl"
    metrics_path = out_dir / "metrics.json"

    rows = load_rows(input_path, args.source_id, args.task_type, args.limit)
    done_ids = load_done_ids(pred_path) if args.resume else set()
    pending = [row for row in rows if row.get("image_id") not in done_ids]

    pipe = build_pipeline(args)
    mode = "a" if args.resume else "w"
    with pred_path.open(mode, encoding="utf-8") as out:
        for idx, row in enumerate(pending, 1):
            image_path = root / str(row["image_path"]).replace("\\", "/")
            gold = row.get("annotation", {}).get("full_ocr_text", "")
            start = time.time()
            error = None
            pred_text = ""
            try:
                predict_kwargs: dict[str, Any] = {}
                if args.max_new_tokens:
                    predict_kwargs["max_new_tokens"] = args.max_new_tokens
                items = list(pipe.predict(str(image_path), **predict_kwargs))
                pred_text = result_text(items[0]) if items else ""
            except Exception as exc:  # keep full-run accounting honest
                error = repr(exc)
            elapsed = time.time() - start
            dist, denom = edit_distance(pred_text, gold)
            rec = {
                "image_id": row["image_id"],
                "image_path": row["image_path"],
                "gold_text": gold,
                "prediction": {"full_ocr_text": pred_text},
                "normalized_gold": norm_text(gold),
                "normalized_prediction": norm_text(pred_text),
                "exact_match": norm_text(pred_text) == norm_text(gold),
                "edit_distance": dist,
                "gold_chars": denom,
                "cer": dist / denom,
                "elapsed_sec": elapsed,
                "error": error,
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            print(
                json.dumps(
                    {
                        "idx": len(done_ids) + idx,
                        "total": len(rows),
                        "image_id": rec["image_id"],
                        "cer": rec["cer"],
                        "exact_match": rec["exact_match"],
                        "elapsed_sec": rec["elapsed_sec"],
                        "error": rec["error"],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    records = []
    with pred_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    records = [row for row in records if row.get("image_id") in {r["image_id"] for r in rows}]

    total_dist = sum(int(r["edit_distance"]) for r in records)
    total_chars = sum(int(r["gold_chars"]) for r in records)
    metrics = {
        "model": args.model_label
        or ("PaddleOCR-VL-1.5" if args.pipeline_version == "v1.5" else f"PaddleOCR-VL {args.pipeline_version}"),
        "pipeline_version": args.pipeline_version,
        "vl_rec_model_dir": args.vl_rec_model_dir,
        "source_id": args.source_id,
        "task_type": args.task_type,
        "subset": "full filtered eval subset" if not args.limit else f"first {args.limit} filtered eval records",
        "disable_layout": args.disable_layout,
        "max_new_tokens": args.max_new_tokens,
        "n_expected": len(rows),
        "n_completed": len(records),
        "errors": sum(1 for r in records if r.get("error")),
        "exact_match_rate": sum(1 for r in records if r.get("exact_match")) / len(records) if records else None,
        "mean_cer": sum(float(r["cer"]) for r in records) / len(records) if records else None,
        "micro_cer": total_dist / total_chars if total_chars else None,
        "mean_elapsed_sec": sum(float(r["elapsed_sec"]) for r in records) / len(records) if records else None,
        "total_elapsed_sec": sum(float(r["elapsed_sec"]) for r in records),
        "note": "OCR on the filtered eval subset. If vl_rec_model_dir is set, this is the exported or merged local model.",
    }
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("METRICS " + json.dumps(metrics, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
