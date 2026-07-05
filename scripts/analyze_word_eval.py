#!/usr/bin/env python3
"""Create error and latency reports from OCR prediction JSONL files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.data.loader import load_jsonl, write_json
from medrxocr.evaluation.analysis import analyze_predictions


def markdown_report(title: str, report: dict) -> str:
    summary = report["summary"]
    latency = report["latency"]
    lines = [
        f"# {title}",
        "",
        "## 总览",
        "",
        f"- 样本数：{summary['n_records']}",
        f"- 可计分样本：{summary['n_scored']}",
        f"- 错误/超时记录：{summary['errors']}",
        f"- Exact Match：{summary['exact_match_rate']:.4f}" if summary["exact_match_rate"] is not None else "- Exact Match：NA",
        f"- Mean CER：{summary['mean_cer']:.4f}" if summary["mean_cer"] is not None else "- Mean CER：NA",
        f"- Micro CER：{summary['micro_cer']:.4f}" if summary["micro_cer"] is not None else "- Micro CER：NA",
        "",
        "## 推理耗时",
        "",
        f"- 平均耗时：{latency['mean_sec']:.2f}s" if latency["mean_sec"] is not None else "- 平均耗时：NA",
        f"- P50：{latency['p50_sec']:.2f}s" if latency["p50_sec"] is not None else "- P50：NA",
        f"- P95：{latency['p95_sec']:.2f}s" if latency["p95_sec"] is not None else "- P95：NA",
        f"- P99：{latency['p99_sec']:.2f}s" if latency["p99_sec"] is not None else "- P99：NA",
        f"- 最慢样本：{latency['max_sec']:.2f}s" if latency["max_sec"] is not None else "- 最慢样本：NA",
        f"- 超过 {latency['slow_threshold_sec']}s 的样本数：{latency['slow_count']}",
        "",
        "## 字符错误",
        "",
    ]
    for key, value in report["char_errors"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## 最差样本", ""])
    for item in report["worst_cer_examples"][:5]:
        lines.append(f"- {item['image_id']}：CER={item['cer']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md")
    parser.add_argument("--title", default="OCR 错误分析")
    parser.add_argument("--slow-threshold-sec", type=float, default=10.0)
    args = parser.parse_args()

    rows = load_jsonl(args.predictions)
    report = analyze_predictions(rows, slow_threshold_sec=args.slow_threshold_sec)
    write_json(args.output_json, report)
    if args.output_md:
        Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_md).write_text(markdown_report(args.title, report), encoding="utf-8")


if __name__ == "__main__":
    main()
