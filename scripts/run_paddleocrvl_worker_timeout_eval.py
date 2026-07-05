#!/usr/bin/env python3
"""Run PaddleOCR-VL with a warm worker and per-image timeouts."""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import queue
import sys
import time
from pathlib import Path
from typing import Any


def norm(text: str | None) -> str:
    return " ".join((text or "").lower().split())


def edit_distance(a: str | None, b: str | None) -> tuple[int, int]:
    a, b = norm(a), norm(b)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1], max(len(b), 1)


def result_text(item: Any) -> str:
    markdown = getattr(item, "markdown", None)
    if isinstance(markdown, str) and markdown.strip():
        return markdown
    data = getattr(item, "json", None)
    if isinstance(data, dict):
        blocks = data.get("res", {}).get("parsing_res_list", [])
        return "\n".join(str(block.get("block_content", "")) for block in blocks)
    return str(item)


def configure_windows_cuda_dlls() -> None:
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


def load_rows(input_path: Path, source_id: str, start: int, limit: int) -> list[dict[str, Any]]:
    rows = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("metadata", {}).get("source_id") == source_id:
                rows.append(row)
    end = len(rows) if not limit else min(len(rows), start + limit)
    return rows[start:end]


def worker_main(config: dict[str, Any], job_q: mp.Queue, result_q: mp.Queue) -> None:
    if config.get("cache_root"):
        cache_root = Path(config["cache_root"])
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(cache_root / "paddlex_cache"))
        os.environ.setdefault("HF_HOME", str(cache_root / "hf_cache"))
        os.environ.setdefault("MODELSCOPE_CACHE", str(cache_root / "modelscope_cache"))
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("PADDLE_PDX_MODEL_SOURCE", config.get("model_source") or "modelscope")
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
    configure_windows_cuda_dlls()

    from paddleocr import PaddleOCRVL

    pipe_kwargs: dict[str, Any] = {"pipeline_version": config["pipeline_version"]}
    if config.get("vl_rec_model_dir"):
        pipe_kwargs["vl_rec_model_dir"] = config["vl_rec_model_dir"]
    if config.get("disable_layout"):
        pipe_kwargs["use_layout_detection"] = False
    pipe = PaddleOCRVL(**pipe_kwargs)
    result_q.put({"type": "ready"})

    root = Path(config["root"])
    while True:
        row = job_q.get()
        if row is None:
            return

        image_path = root / str(row["image_path"]).replace("\\", "/")
        gold = row.get("annotation", {}).get("full_ocr_text", "")
        start = time.time()
        error = None
        pred_text = ""
        try:
            predict_kwargs: dict[str, Any] = {}
            if config.get("max_new_tokens"):
                predict_kwargs["max_new_tokens"] = config["max_new_tokens"]
            items = list(pipe.predict(str(image_path), **predict_kwargs))
            pred_text = result_text(items[0]) if items else ""
        except Exception as exc:
            error = repr(exc)

        elapsed = time.time() - start
        dist, denom = edit_distance(pred_text, gold)
        result_q.put(
            {
                "type": "result",
                "record": {
                    "image_id": row["image_id"],
                    "image_path": row["image_path"],
                    "gold_text": gold,
                    "prediction": {"full_ocr_text": pred_text},
                    "cer": dist / denom,
                    "elapsed_sec": elapsed,
                    "error": error,
                    "max_new_tokens": config.get("max_new_tokens"),
                    "disable_layout": config.get("disable_layout", False),
                },
            }
        )


def start_worker(ctx: mp.context.BaseContext, config: dict[str, Any], load_timeout_sec: int):
    job_q = ctx.Queue()
    result_q = ctx.Queue()
    proc = ctx.Process(target=worker_main, args=(config, job_q, result_q))
    proc.start()
    try:
        msg = result_q.get(timeout=load_timeout_sec)
    except queue.Empty:
        proc.terminate()
        proc.join(timeout=10)
        raise TimeoutError(f"worker_load_timeout_after_{load_timeout_sec}s")
    if msg.get("type") != "ready":
        proc.terminate()
        proc.join(timeout=10)
        raise RuntimeError(f"worker failed before ready: {msg!r}")
    return proc, job_q, result_q


def stop_worker(proc: mp.Process, job_q: mp.Queue | None) -> None:
    if proc.is_alive() and job_q is not None:
        try:
            job_q.put(None)
        except Exception:
            pass
        proc.join(timeout=5)
    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=10)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--input", default="data/eval/realshot_eval_18.jsonl")
    p.add_argument("--output-dir", default="outputs/paddleocrvl_worker_timeout_eval")
    p.add_argument("--source-id", default="realshot_mendeley_bilingual_1000")
    p.add_argument("--pipeline-version", default="v1")
    p.add_argument("--vl-rec-model-dir", default=None)
    p.add_argument("--model-label", default=None)
    p.add_argument("--max-new-tokens", type=int, default=None)
    p.add_argument("--disable-layout", action="store_true")
    p.add_argument("--cache-root", default="C:\\pocr_cache_ms")
    p.add_argument("--model-source", default="modelscope")
    p.add_argument("--timeout-sec", type=int, default=60)
    p.add_argument("--load-timeout-sec", type=int, default=180)
    p.add_argument("--retries", type=int, default=1)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "predictions.jsonl"
    metrics_path = out_dir / "metrics.json"

    rows = load_rows(Path(args.input), args.source_id, args.start, args.limit)
    config = vars(args).copy()
    ctx = mp.get_context("spawn")
    proc = None
    job_q = None
    result_q = None
    records = []

    try:
        proc, job_q, result_q = start_worker(ctx, config, args.load_timeout_sec)
        with pred_path.open("w", encoding="utf-8") as pred_file:
            for index, row in enumerate(rows, args.start + 1):
                attempts = []
                rec = None
                status = "TIMEOUT"
                for attempt in range(args.retries + 1):
                    assert job_q is not None and result_q is not None and proc is not None
                    job_q.put(row)
                    try:
                        msg = result_q.get(timeout=args.timeout_sec)
                        rec = msg["record"]
                        attempts.append(
                            {
                                "attempt": attempt + 1,
                                "status": "done" if not rec.get("error") else "error",
                                "elapsed_sec": rec.get("elapsed_sec"),
                                "error": rec.get("error"),
                            }
                        )
                        status = "DONE" if not rec.get("error") else "ERROR"
                        break
                    except queue.Empty:
                        stop_worker(proc, None)
                        attempts.append(
                            {
                                "attempt": attempt + 1,
                                "status": "timeout",
                                "elapsed_sec": args.timeout_sec,
                                "error": f"timeout_after_{args.timeout_sec}s",
                            }
                        )
                        if attempt < args.retries:
                            proc, job_q, result_q = start_worker(ctx, config, args.load_timeout_sec)
                            continue
                        rec = {
                            "image_id": row["image_id"],
                            "image_path": row["image_path"],
                            "gold_text": row.get("annotation", {}).get("full_ocr_text", ""),
                            "prediction": {"full_ocr_text": ""},
                            "cer": None,
                            "elapsed_sec": args.timeout_sec,
                            "error": f"timeout_after_{args.timeout_sec}s",
                            "max_new_tokens": args.max_new_tokens,
                            "disable_layout": args.disable_layout,
                        }
                        status = "TIMEOUT"
                        proc, job_q, result_q = start_worker(ctx, config, args.load_timeout_sec)

                assert rec is not None
                rec["attempts"] = attempts

                pred_file.write(json.dumps(rec, ensure_ascii=False) + "\n")
                pred_file.flush()
                records.append(rec)
                print(
                    json.dumps(
                        {
                            "status": status,
                            "index": index,
                            "image_id": rec["image_id"],
                            "cer": rec.get("cer"),
                            "elapsed_sec": rec.get("elapsed_sec"),
                            "error": rec.get("error"),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
    finally:
        if proc is not None:
            stop_worker(proc, job_q)

    completed = [r for r in records if r.get("cer") is not None and not r.get("error")]
    total_dist = 0
    total_chars = 0
    for rec in completed:
        dist, denom = edit_distance(rec.get("prediction", {}).get("full_ocr_text", ""), rec.get("gold_text", ""))
        total_dist += dist
        total_chars += denom

    metrics = {
        "model": args.model_label or "PaddleOCR-VL",
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
        "load_timeout_sec": args.load_timeout_sec,
        "retries": args.retries,
        "note": "The model is loaded once per worker. Per-image timeout starts after worker readiness.",
    }
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("METRICS " + json.dumps(metrics, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
