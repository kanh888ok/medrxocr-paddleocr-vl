# LoRA SFT Runbook

This runbook tracks the remaining fine-tuning work. It follows the PaddleOCR-VL
SFT path that uses ERNIEKit-style `image_info` and `text_info` JSONL records.

## 1. Build ERNIEKit SFT Manifests

```bash
python scripts/build_erniekit_vl_sft_manifest.py \
  --input data/processed/medrxocr_train.jsonl \
  --output data/processed/train_rx_erniekit_sft.jsonl

python scripts/build_erniekit_vl_sft_manifest.py \
  --input data/processed/medrxocr_val.jsonl \
  --output data/processed/val_rx_erniekit_sft.jsonl

python scripts/build_erniekit_vl_sft_manifest.py \
  --input data/processed/medrxocr_eval.jsonl \
  --output data/processed/eval_rx_erniekit_sft.jsonl
```

## 2. Training Config

Draft config:

```text
configs/erniekit_paddleocr_vl_lora_medrxocr.yaml
```

This config is a first-pass LoRA SFT run for a single GPU. It should be treated
as a smoke training configuration until a checkpoint is produced and evaluated.

## 3. Required Training Outputs

The submission should not claim SFT completion until all of these exist:

- `outputs/medrxocr_lora/` training logs.
- A LoRA adapter or checkpoint directory.
- A model/checkpoint URL from Hugging Face, AI Studio, or Baidu Netdisk.
- Validation metrics from the trained checkpoint.
- Eval predictions and metrics, preferably at least on the RxHandBD word-level
  eval subset and one full-page prescription subset.

## 4. Current Status

Completed:

- Zero-shot PaddleOCR-VL full RxHandBD word-level eval.
- Zero-shot PaddleOCR-VL-1.5 full RxHandBD word-level eval.
- ERNIEKit SFT manifest builder.
- LoRA SFT config draft.

Not completed:

- ERNIEKit runtime installation verification.
- Actual LoRA SFT training.
- Checkpoint publication.
- Fine-tuned evaluation.

## 5. Truthfulness Note

Until a checkpoint is trained and evaluated, describe this repository as a
MedRxOCR data/evaluation protocol with PaddleOCR-VL zero-shot baselines and a
prepared LoRA SFT pipeline. Do not describe it as a completed fine-tuned
derivative model.
