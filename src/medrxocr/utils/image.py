"""Image inspection helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def image_info(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    info: dict[str, Any] = {
        "exists": path.exists(),
        "path": str(path),
        "file_kb": round(path.stat().st_size / 1024, 2) if path.exists() else None,
        "width": None,
        "height": None,
        "megapixels": None,
    }
    if not path.exists():
        return info
    try:
        from PIL import Image

        with Image.open(path) as img:
            width, height = img.size
        info.update(
            {
                "width": width,
                "height": height,
                "megapixels": round(width * height / 1_000_000, 3),
            }
        )
    except Exception as exc:
        info["image_error"] = repr(exc)
    return info
