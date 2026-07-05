#!/usr/bin/env python3
"""Manually merge a PaddleOCR-VL LoRA adapter into the base model."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import paddle
from paddleformers.peft import LoRAModel
from safetensors import safe_open

from ernie.modeling_paddleocr_vl import PaddleOCRVLForConditionalGeneration


COPY_FILES = [
    "added_tokens.json",
    "chat_template.jinja",
    "generation_config.json",
    "inference.yml",
    "preprocessor_config.json",
    "special_tokens_map.json",
    "tokenizer.model",
    "tokenizer_config.json",
]


def copy_runtime_files(base_dir: Path, adapter_dir: Path, output_dir: Path) -> list[str]:
    copied: list[str] = []
    for name in COPY_FILES:
        for src_root in (adapter_dir, base_dir):
            src = src_root / name
            if src.exists():
                shutil.copy2(src, output_dir / name)
                copied.append(name)
                break
    return copied


def load_safetensor_keys(path: Path) -> set[str]:
    with safe_open(str(path), framework="np") as f:
        return set(f.keys())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", default="../work/PaddlePaddle/PaddleOCR-VL")
    parser.add_argument("--adapter", default="outputs/medrxocr_lora_word_win4070/word100_20260705")
    parser.add_argument("--output", default="outputs/medrxocr_lora_word_win4070/word100_20260705_merged_hf")
    parser.add_argument("--device", default="gpu")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--max-shard-size", default="5GB")
    parser.add_argument("--safe-serialization", action="store_true")
    parser.add_argument("--convert-from-hf", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-to-hf", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--strip-lora", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--match-base-keys", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    start = time.time()
    base_dir = Path(args.base_model)
    adapter_dir = Path(args.adapter)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    paddle.set_device(args.device)
    model = PaddleOCRVLForConditionalGeneration.from_pretrained(
        str(base_dir),
        dtype=args.dtype,
        convert_from_hf=args.convert_from_hf,
    )
    lora_model = LoRAModel.from_pretrained(model=model, lora_path=str(adapter_dir))
    lora_model.merge()
    model_to_save = lora_model.restore_original_model() if args.strip_lora else lora_model.model
    state_dict = None
    removed_keys: list[str] = []
    base_weights_path = base_dir / "model.safetensors"
    if args.match_base_keys and base_weights_path.exists():
        base_keys = load_safetensor_keys(base_weights_path)
        current_state_dict = model_to_save.state_dict()
        removed_keys = sorted(k for k in current_state_dict if k not in base_keys)
        state_dict = {k: v for k, v in current_state_dict.items() if k in base_keys}
    model_to_save.save_pretrained(
        str(output_dir),
        state_dict=state_dict,
        max_shard_size=args.max_shard_size,
        safe_serialization=args.safe_serialization,
        save_to_hf=args.save_to_hf,
    )
    copied = copy_runtime_files(base_dir, adapter_dir, output_dir)

    summary = {
        "status": "completed",
        "base_model": str(base_dir),
        "adapter": str(adapter_dir),
        "output": str(output_dir),
        "dtype": args.dtype,
        "convert_from_hf": args.convert_from_hf,
        "save_to_hf": args.save_to_hf,
        "strip_lora": args.strip_lora,
        "match_base_keys": args.match_base_keys,
        "removed_extra_keys": removed_keys,
        "safe_serialization": args.safe_serialization,
        "copied_runtime_files": copied,
        "elapsed_sec": round(time.time() - start, 3),
    }
    (output_dir / "merge_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
