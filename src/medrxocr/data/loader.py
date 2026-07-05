"""JSONL loaders used by scripts and tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def iter_jsonl(path: str | Path) -> Iterable[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return list(iter_jsonl(path))


def write_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def filter_records(
    rows: Iterable[dict[str, Any]],
    source_id: str | None = None,
    task_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        metadata = row.get("metadata", {})
        if source_id and metadata.get("source_id") != source_id:
            continue
        if task_type and metadata.get("task_type") != task_type:
            continue
        selected.append(row)
        if limit and len(selected) >= limit:
            break
    return selected


def annotation_text(row: dict[str, Any]) -> str:
    return str(row.get("annotation", {}).get("full_ocr_text", ""))
