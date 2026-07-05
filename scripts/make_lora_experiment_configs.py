#!/usr/bin/env python3
"""Generate small LoRA experiment configs from the current step512 config."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def replace_yaml_scalar(text: str, key: str, value: str | int | float) -> str:
    line = f"{key}: {value}"
    pattern = rf"(?m)^{re.escape(key)}:\s*.+$"
    if re.search(pattern, text):
        return re.sub(pattern, line, text)
    return text.rstrip() + "\n" + line + "\n"


def write_config(base_text: str, output: Path, replacements: dict[str, str | int | float]) -> None:
    text = base_text
    for key, value in replacements.items():
        text = replace_yaml_scalar(text, key, value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")


def quoted(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-config", default="configs/erniekit_paddleocr_vl_lora_word_full_ocrprompt_lr2e5_win4070.yaml")
    parser.add_argument("--output-dir", default="configs/experiments")
    args = parser.parse_args()

    base_path = Path(args.base_config)
    base_text = base_path.read_text(encoding="utf-8")
    out_dir = Path(args.output_dir)

    experiments = {
        "rank4": {
            "lora_rank": 4,
            "output_dir": quoted("./outputs/medrxocr_lora_rank4_win4070/checkpoint_run"),
            "logging_dir": quoted("./outputs/medrxocr_lora_rank4_win4070/checkpoint_run/visualdl_logs"),
        },
        "rank16": {
            "lora_rank": 16,
            "output_dir": quoted("./outputs/medrxocr_lora_rank16_win4070/checkpoint_run"),
            "logging_dir": quoted("./outputs/medrxocr_lora_rank16_win4070/checkpoint_run/visualdl_logs"),
        },
        "aug_rank8": {
            "lora_rank": 8,
            "train_dataset_path": quoted("./data/processed/train_rx_erniekit_sft_word_aug_camera.jsonl"),
            "num_samples_each_epoch": 19895,
            "output_dir": quoted("./outputs/medrxocr_lora_aug_rank8_win4070/checkpoint_run"),
            "logging_dir": quoted("./outputs/medrxocr_lora_aug_rank8_win4070/checkpoint_run/visualdl_logs"),
        },
        "hard_focus_rank8": {
            "lora_rank": 8,
            "train_dataset_path": quoted("./data/processed/train_rx_erniekit_sft_word_hard512.jsonl"),
            "num_samples_each_epoch": 512,
            "max_steps": 256,
            "save_steps": 128,
            "eval_steps": 128,
            "warmup_steps": 10,
            "learning_rate": "1.0e-5",
            "min_lr": "1.0e-6",
            "output_dir": quoted("./outputs/medrxocr_lora_hard_focus_rank8_win4070/checkpoint_run"),
            "logging_dir": quoted("./outputs/medrxocr_lora_hard_focus_rank8_win4070/checkpoint_run/visualdl_logs"),
        },
    }

    for name, replacements in experiments.items():
        output = out_dir / f"erniekit_paddleocr_vl_lora_word_{name}_win4070.yaml"
        write_config(base_text, output, replacements)
        print(output)


if __name__ == "__main__":
    main()
