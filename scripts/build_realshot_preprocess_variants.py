#!/usr/bin/env python3
"""Build fixed preprocessing variants for the real-shot eval subset."""

import argparse
import copy
import json
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


VARIANT_STEPS = {
    "resize_long_1280": [
        "convert_rgb",
        "resize_long_edge_to_1280",
    ],
    "contrast_sharp_1280": [
        "convert_rgb",
        "autocontrast_cutoff_1",
        "contrast_1.10",
        "sharpness_1.30",
        "resize_long_edge_to_1280",
    ],
    "gray_autocontrast_sharp_1280": [
        "grayscale",
        "autocontrast_cutoff_1",
        "contrast_1.15",
        "sharpness_1.40",
        "resize_long_edge_to_1280",
        "convert_rgb",
    ],
}


def load_rows(path, source_id):
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("metadata", {}).get("source_id") == source_id:
                rows.append(row)
    return rows


def resize_long_edge(img, max_long):
    width, height = img.size
    long_edge = max(width, height)
    if long_edge <= max_long:
        return img
    scale = max_long / long_edge
    new_size = (round(width * scale), round(height * scale))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def apply_variant(img, variant):
    if variant == "resize_long_1280":
        img = img.convert("RGB")
        return resize_long_edge(img, 1280)

    if variant == "contrast_sharp_1280":
        img = img.convert("RGB")
        img = ImageOps.autocontrast(img, cutoff=1)
        img = ImageEnhance.Contrast(img).enhance(1.10)
        img = ImageEnhance.Sharpness(img).enhance(1.30)
        return resize_long_edge(img, 1280)

    if variant == "gray_autocontrast_sharp_1280":
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img, cutoff=1)
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.40)
        img = resize_long_edge(img, 1280)
        return img.convert("RGB")

    raise ValueError(f"Unknown variant: {variant}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--input", default="data/eval/realshot_eval_18.jsonl")
    p.add_argument("--source-id", default="realshot_mendeley_bilingual_1000")
    p.add_argument("--output-root", default="data/eval/realshot_preprocessed")
    p.add_argument("--manifest-dir", default="data/eval")
    p.add_argument(
        "--variants",
        default="resize_long_1280,contrast_sharp_1280,gray_autocontrast_sharp_1280",
        help="Comma-separated variant names.",
    )
    p.add_argument("--jpeg-quality", type=int, default=92)
    args = p.parse_args()

    root = Path(args.root)
    output_root = Path(args.output_root)
    manifest_dir = Path(args.manifest_dir)
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    rows = load_rows(args.input, args.source_id)

    summary = {
        "input": args.input,
        "source_id": args.source_id,
        "n_images": len(rows),
        "variants": {},
    }

    for variant in variants:
        if variant not in VARIANT_STEPS:
            raise SystemExit(f"Unknown variant: {variant}")

        variant_dir = output_root / variant
        variant_dir.mkdir(parents=True, exist_ok=True)
        out_manifest = manifest_dir / f"realshot_eval_18_{variant}.jsonl"
        out_rows = []

        for row in rows:
            src_rel = Path(str(row["image_path"]).replace("\\", "/"))
            src_path = root / src_rel
            dst_rel = Path(args.output_root) / variant / src_rel.name
            dst_path = root / dst_rel

            with Image.open(src_path) as img:
                original_size = list(img.size)
                processed = apply_variant(img, variant)
                processed_size = list(processed.size)
                processed.save(dst_path, format="JPEG", quality=args.jpeg_quality, optimize=True)

            new_row = copy.deepcopy(row)
            new_row["image_path"] = dst_rel.as_posix()
            metadata = new_row.setdefault("metadata", {})
            metadata["preprocess_variant"] = variant
            metadata["preprocess_from"] = row["image_path"]
            metadata["preprocess_steps"] = VARIANT_STEPS[variant]
            metadata["original_image_size"] = original_size
            metadata["processed_image_size"] = processed_size
            out_rows.append(new_row)

        with out_manifest.open("w", encoding="utf-8") as f:
            for row in out_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        summary["variants"][variant] = {
            "manifest": out_manifest.as_posix(),
            "image_dir": variant_dir.as_posix(),
            "steps": VARIANT_STEPS[variant],
            "n_images": len(out_rows),
        }

    summary_path = manifest_dir / "realshot_preprocess_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
