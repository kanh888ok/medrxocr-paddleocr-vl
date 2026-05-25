# LoRA/SFT Runbook

This runbook describes the MedRxOCR LoRA/SFT artifact path used for the
challenge submission and the commands needed to regenerate the SFT manifests.

## Released Checkpoint

The lightweight initial MedRxOCR LoRA/SFT derivative checkpoint is released at:

`https://aistudio.baidu.com/dataset/detail/384021/intro`

The checkpoint is intended for research evaluation in the challenge setting. It
is not intended for direct clinical deployment.

## Build ERNIEKit SFT Manifests

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

## Training Config

The repository includes a single-GPU LoRA/SFT configuration:

```text
configs/erniekit_paddleocr_vl_lora_medrxocr.yaml
```

## Included Evaluation Baselines

- PaddleOCR-VL full RxHandBD word-level zero-shot evaluation.
- PaddleOCR-VL-1.5 full RxHandBD word-level zero-shot evaluation.
- Metrics JSON and predictions JSONL artifacts under `outputs/`.

## Reporting Scope

The published metric table should be described as zero-shot word-level OCR
baseline results. The released checkpoint should be described separately as a
lightweight initial domain-adapted PaddleOCR-VL derivative checkpoint for the
MedRxOCR task.
