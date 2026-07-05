#!/usr/bin/env python3
"""Run a PaddleOCR-VL zero-shot OCR pilot on MedRxOCR eval data.

This script is intended for GPU environments with PaddleOCR installed:

python scripts/run_paddleocrvl_zero_shot.py \
  --root . \
  --input data/processed/medrxocr_eval.jsonl \
  --output-dir outputs/paddleocrvl_v15_pilot \
  --source-id mendeley_bilingual_1000 \
  --limit 5 \
  --pipeline-version v1.5
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path


def norm(text):
    return " ".join((text or "").lower().split())


def edit_distance(a, b):
    a, b = norm(a), norm(b)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1], max(len(b), 1)


def result_text(item):
    markdown = getattr(item, "markdown", None)
    if isinstance(markdown, str) and markdown.strip():
        return markdown
    data = getattr(item, "json", None)
    if isinstance(data, dict):
        blocks = data.get("res", {}).get("parsing_res_list", [])
        return "\n".join(str(block.get("block_content", "")) for block in blocks)
    return str(item)


def configure_windows_cuda_dlls():
    if os.name != "nt":
        return
    site_packages = Path(sys.prefix) / "Lib" / "site-packages"
    candidates = [
        site_packages / "nvidia" / "cu13" / "bin" / "x86_64",
        site_packages / "nvidia" / "cu13" / "lib" / "x64",
        site_packages / "nvidia" / "cudnn" / "bin",
    ]
    existing = [str(path) for path in candidates if path.exists()]
    if not existing:
        return
    os.environ["PATH"] = os.pathsep.join(existing + [os.environ.get("PATH", "")])
    for path in existing:
        try:
            os.add_dll_directory(path)
        except (AttributeError, OSError):
            pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--input", default="data/processed/medrxocr_eval.jsonl")
    p.add_argument("--output-dir", default="outputs/paddleocrvl_v15_pilot")
    p.add_argument("--source-id", default="mendeley_bilingual_1000")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--pipeline-version", default="v1.5")
    p.add_argument("--vl-rec-model-dir", default=None)
    p.add_argument("--model-label", default=None)
    p.add_argument("--max-new-tokens", type=int, default=None)
    p.add_argument("--disable-layout", action="store_true")
    p.add_argument("--cache-root", default=None)
    p.add_argument("--model-source", default="modelscope")
    args = p.parse_args()

    if args.cache_root:
        cache_root = Path(args.cache_root)
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(cache_root / "paddlex_cache"))
        os.environ.setdefault("HF_HOME", str(cache_root / "hf_cache"))
        os.environ.setdefault("MODELSCOPE_CACHE", str(cache_root / "modelscope_cache"))
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("PADDLE_PDX_MODEL_SOURCE", args.model_source)
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
    configure_windows_cuda_dlls()

    from paddleocr import PaddleOCRVL

    root = Path(args.root)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "predictions.jsonl"
    metrics_path = out_dir / "metrics.json"

    rows = []
    matched = 0
    with Path(args.input).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("metadata", {}).get("source_id") == args.source_id:
                if matched < args.offset:
                    matched += 1
                    continue
                rows.append(row)
                matched += 1
            if args.limit and len(rows) >= args.limit:
                break

    pipe_kwargs = {"pipeline_version": args.pipeline_version}
    if args.vl_rec_model_dir:
        pipe_kwargs["vl_rec_model_dir"] = args.vl_rec_model_dir
    if args.disable_layout:
        pipe_kwargs["use_layout_detection"] = False
    pipe = PaddleOCRVL(**pipe_kwargs)
    records = []
    total_dist = 0
    total_chars = 0

    with pred_path.open("w", encoding="utf-8") as g:
        for row in rows:
            image_path = root / row["image_path"].replace("\\", "/")
            gold = row.get("annotation", {}).get("full_ocr_text", "")
            start = time.time()
            error = None
            pred_text = ""
            try:
                predict_kwargs = {}
                if args.max_new_tokens:
                    predict_kwargs["max_new_tokens"] = args.max_new_tokens
                items = list(pipe.predict(str(image_path), **predict_kwargs))
                pred_text = result_text(items[0]) if items else ""
            except Exception as exc:
                error = repr(exc)
            elapsed = time.time() - start
            dist, denom = edit_distance(pred_text, gold)
            total_dist += dist
            total_chars += denom
            rec = {
                "image_id": row["image_id"],
                "image_path": row["image_path"],
                "gold_text": gold,
                "prediction": {"full_ocr_text": pred_text},
                "cer": dist / denom,
                "elapsed_sec": elapsed,
                "error": error,
                "max_new_tokens": args.max_new_tokens,
                "disable_layout": args.disable_layout,
            }
            g.write(json.dumps(rec, ensure_ascii=False) + "\n")
            g.flush()
            records.append(rec)
            print(json.dumps({k: rec[k] for k in ["image_id", "cer", "elapsed_sec", "error"]}, ensure_ascii=False), flush=True)

    metrics = {
        "model": args.model_label
        or ("PaddleOCR-VL-1.5" if args.pipeline_version == "v1.5" else f"PaddleOCR-VL {args.pipeline_version}"),
        "pipeline_version": args.pipeline_version,
        "vl_rec_model_dir": args.vl_rec_model_dir,
        "max_new_tokens": args.max_new_tokens,
        "disable_layout": args.disable_layout,
        "source_id": args.source_id,
        "n_images": len(records),
        "mean_cer": sum(r["cer"] for r in records) / len(records) if records else None,
        "micro_cer": total_dist / total_chars if total_chars else None,
        "mean_elapsed_sec": sum(r["elapsed_sec"] for r in records) / len(records) if records else None,
        "errors": sum(1 for r in records if r["error"]),
        "model_source": args.model_source,
        "note": "Report together with split name and image count; real-shot eval uses photographed replacements of public eval images.",
    }
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("METRICS " + json.dumps(metrics, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
