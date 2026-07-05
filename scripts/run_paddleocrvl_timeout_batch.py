#!/usr/bin/env python3
"""Run PaddleOCR-VL eval one image at a time with a timeout per image."""

import argparse
import json
import subprocess
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


def load_rows(input_path, source_id):
    rows = []
    with Path(input_path).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("metadata", {}).get("source_id") == source_id:
                rows.append(row)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--python-exe", default=sys.executable)
    p.add_argument("--root", default=".")
    p.add_argument("--input", default="data/eval/realshot_eval_18.jsonl")
    p.add_argument("--output-dir", default="outputs/paddleocrvl_v15_realshot_eval18_gpu_timeout")
    p.add_argument("--source-id", default="realshot_mendeley_bilingual_1000")
    p.add_argument("--pipeline-version", default="v1.5")
    p.add_argument("--vl-rec-model-dir", default=None)
    p.add_argument("--model-label", default=None)
    p.add_argument("--max-new-tokens", type=int, default=None)
    p.add_argument("--disable-layout", action="store_true")
    p.add_argument("--cache-root", default="C:\\pocr_cache_ms")
    p.add_argument("--model-source", default="modelscope")
    p.add_argument("--timeout-sec", type=int, default=120)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    rows = load_rows(args.input, args.source_id)
    end = len(rows) if not args.limit else min(len(rows), args.start + args.limit)
    selected = rows[args.start:end]

    out_dir = Path(args.output_dir)
    child_dir = out_dir / "per_image"
    out_dir.mkdir(parents=True, exist_ok=True)
    child_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "predictions.jsonl"
    metrics_path = out_dir / "metrics.json"

    records = []
    total_dist = 0
    total_chars = 0

    with pred_path.open("w", encoding="utf-8") as pred_file:
        for local_i, row in enumerate(selected):
            offset = args.start + local_i
            image_id = row["image_id"]
            one_dir = child_dir / f"{offset + 1:02d}_{image_id}"
            one_dir.mkdir(parents=True, exist_ok=True)
            start = time.time()
            cmd = [
                args.python_exe,
                "scripts/run_paddleocrvl_zero_shot.py",
                "--root",
                args.root,
                "--input",
                args.input,
                "--output-dir",
                str(one_dir),
                "--source-id",
                args.source_id,
                "--offset",
                str(offset),
                "--limit",
                "1",
                "--pipeline-version",
                args.pipeline_version,
                "--cache-root",
                args.cache_root,
                "--model-source",
                args.model_source,
            ]
            if args.vl_rec_model_dir:
                cmd.extend(["--vl-rec-model-dir", args.vl_rec_model_dir])
            if args.model_label:
                cmd.extend(["--model-label", args.model_label])
            if args.max_new_tokens:
                cmd.extend(["--max-new-tokens", str(args.max_new_tokens)])
            if args.disable_layout:
                cmd.append("--disable-layout")
            stdout_path = one_dir / "subprocess.out.log"
            stderr_path = one_dir / "subprocess.err.log"
            try:
                with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open(
                    "w", encoding="utf-8"
                ) as err:
                    subprocess.run(cmd, stdout=out, stderr=err, timeout=args.timeout_sec, check=False)
                child_pred = one_dir / "predictions.jsonl"
                if child_pred.exists() and child_pred.stat().st_size:
                    rec = json.loads(child_pred.read_text(encoding="utf-8").splitlines()[-1])
                else:
                    rec = {
                        "image_id": image_id,
                        "image_path": row["image_path"],
                        "gold_text": row.get("annotation", {}).get("full_ocr_text", ""),
                        "prediction": {"full_ocr_text": ""},
                        "cer": None,
                        "elapsed_sec": time.time() - start,
                        "error": "no_prediction_written",
                        "max_new_tokens": args.max_new_tokens,
                        "disable_layout": args.disable_layout,
                    }
            except subprocess.TimeoutExpired:
                rec = {
                    "image_id": image_id,
                    "image_path": row["image_path"],
                    "gold_text": row.get("annotation", {}).get("full_ocr_text", ""),
                    "prediction": {"full_ocr_text": ""},
                    "cer": None,
                    "elapsed_sec": time.time() - start,
                    "error": f"timeout_after_{args.timeout_sec}s",
                    "max_new_tokens": args.max_new_tokens,
                    "disable_layout": args.disable_layout,
                }

            if rec.get("cer") is None and not rec.get("error"):
                dist, denom = edit_distance(
                    rec.get("prediction", {}).get("full_ocr_text", ""),
                    rec.get("gold_text", ""),
                )
                rec["cer"] = dist / denom
            if rec.get("cer") is not None:
                pred_text = rec.get("prediction", {}).get("full_ocr_text", "")
                gold = rec.get("gold_text", "")
                dist, denom = edit_distance(pred_text, gold)
                total_dist += dist
                total_chars += denom

            pred_file.write(json.dumps(rec, ensure_ascii=False) + "\n")
            pred_file.flush()
            records.append(rec)
            error_text = str(rec.get("error") or "")
            status = "TIMEOUT" if error_text.startswith("timeout_after") else "DONE"
            print(
                json.dumps(
                    {
                        "status": status,
                        "index": offset + 1,
                        "image_id": image_id,
                        "cer": rec.get("cer"),
                        "elapsed_sec": rec.get("elapsed_sec"),
                        "error": rec.get("error"),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    completed = [r for r in records if r.get("cer") is not None and not r.get("error")]
    metrics = {
        "model": args.model_label or "PaddleOCR-VL-1.5",
        "pipeline_version": args.pipeline_version,
        "vl_rec_model_dir": args.vl_rec_model_dir,
        "max_new_tokens": args.max_new_tokens,
        "disable_layout": args.disable_layout,
        "source_id": args.source_id,
        "n_images": len(records),
        "completed_images": len(completed),
        "timeout_images": sum(1 for r in records if str(r.get("error", "")).startswith("timeout_after")),
        "error_images": sum(1 for r in records if r.get("error")),
        "mean_cer_completed": sum(r["cer"] for r in completed) / len(completed) if completed else None,
        "micro_cer_completed": total_dist / total_chars if total_chars else None,
        "mean_elapsed_sec_completed": sum(r["elapsed_sec"] for r in completed) / len(completed)
        if completed
        else None,
        "timeout_sec": args.timeout_sec,
        "note": "Timeout records are excluded from CER averages and should be reported separately.",
    }
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("METRICS " + json.dumps(metrics, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
