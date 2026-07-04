#!/usr/bin/env python3
"""Check whether the local environment can start LoRA/SFT training."""

import argparse
import importlib.util
import json
from pathlib import Path


TRAINING_MODULES = ["erniekit", "paddlenlp", "paddlemix", "visualdl"]
RUNTIME_MODULES = ["paddle", "paddleocr"]
REQUIRED_FILES = [
    "data/processed/medrxocr_train.jsonl",
    "data/processed/medrxocr_val.jsonl",
    "data/processed/train_rx_erniekit_sft.jsonl",
    "data/processed/val_rx_erniekit_sft.jsonl",
    "configs/erniekit_paddleocr_vl_lora_medrxocr.yaml",
]


def module_status(names):
    return {name: importlib.util.find_spec(name) is not None for name in names}


def file_status(paths):
    result = {}
    for path in paths:
        p = Path(path)
        result[path] = {
            "exists": p.exists(),
            "size": p.stat().st_size if p.exists() else None,
        }
    return result


def paddle_status():
    try:
        import paddle

        return {
            "available": True,
            "version": getattr(paddle, "__version__", None),
            "compiled_with_cuda": bool(paddle.is_compiled_with_cuda()),
            "device": str(paddle.device.get_device()),
        }
    except Exception as exc:
        return {"available": False, "error": repr(exc)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="")
    args = p.parse_args()

    runtime = module_status(RUNTIME_MODULES)
    training = module_status(TRAINING_MODULES)
    files = file_status(REQUIRED_FILES)
    missing_training_modules = [name for name, ok in training.items() if not ok]
    missing_files = [path for path, info in files.items() if not info["exists"]]

    report = {
        "runtime_modules": runtime,
        "training_modules": training,
        "paddle": paddle_status(),
        "required_files": files,
        "can_start_lora_sft": not missing_training_modules and not missing_files,
        "missing_training_modules": missing_training_modules,
        "missing_files": missing_files,
        "note": "Inference evaluation can run in this environment, but LoRA/SFT needs training dependencies and processed manifests.",
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
