# Submission Completion Plan

This file tracks what remains before a truthful final competition submission.

## Already Done Locally

- Public data sources downloaded and SHA256 verified.
- Raw data normalized into `data/interim/*.jsonl`.
- Fixed train/validation/evaluation splits created in `data/processed/`.
- SFT manifests created:
  - `data/processed/train_rx_sft.jsonl`
  - `data/processed/val_rx_sft.jsonl`
  - `data/processed/eval_rx_sft.jsonl`
- Quality reports generated in `outputs/`.
- Dataset card and technical report updated with the real 997-record Mendeley
  bilingual integrity note.

## Remaining Work Before Final Submission

### 1. PaddleOCR-VL Zero-Shot

Goal: run the official PaddleOCR-VL pipeline on `data/processed/medrxocr_eval.jsonl`.

Required output:

- `outputs/pred_paddleocr_vl_zero_shot.jsonl`
- `outputs/eval_paddleocr_vl_zero_shot.json`
- A short result table added to `docs/technical_report.md`

Notes:

- Use the full PaddleOCR-VL pipeline where possible, not only the VLM component.
- Record exact runtime environment, model name, and command used.

### 2. PaddleOCR-VL-1.5 Zero-Shot

Goal: run PaddleOCR-VL-1.5 on the same fixed eval split.

Current status:

- Single-image smoke test completed on `rx_mendeley_bilingual_1000_0003`.
- This is not a full benchmark.
- The observed smoke-test CER was `10.8082`, with severe repetition/garbled text.
- A 5-image pilot attempt was stopped after more than 30 minutes without a first
  prediction being written.

Required output:

- `outputs/pred_paddleocr_vl_1_5_zero_shot.jsonl`
- `outputs/eval_paddleocr_vl_1_5_zero_shot.json`
- A comparable result table in `docs/technical_report.md`

### 3. LoRA SFT

Goal: fine-tune the VLM component using the generated SFT manifests.

Required output:

- Training logs in `outputs/medrxocr_lora/`
- Final adapter/checkpoint artifact
- Validation metrics
- Evaluation predictions and metrics:
  - `outputs/pred_medrxocr_lora.jsonl`
  - `outputs/eval_medrxocr_lora.json`

Important truthfulness note:

- Official PaddleOCR-VL documentation recommends ERNIEKit SFT for the VLM
  component. Do not claim layout analysis or ranking models were fine-tuned
  unless that is actually done and supported by the selected toolchain.

### 4. Public Repository

Required from user:

- GitHub username or organization.
- Repository name.
- Whether the repository should be public immediately.

Do not commit raw large datasets to GitHub unless license and size policies are
checked. Prefer publishing source registry, scripts, docs, small examples, and
download/processing instructions.

### 5. Public Dataset URL

Required from user:

- AI Studio dataset upload permission, or
- Baidu Netdisk upload destination.

Recommended dataset package:

- `data/processed/*.jsonl`
- `outputs/quality_report_*.json`
- `outputs/dataset_stats_*.json`
- `docs/data_source_registry.*`
- Raw archive checksums

Raw images can be linked back to original Mendeley URLs instead of republished,
unless the competition specifically requires uploading the processed dataset
with images and the license terms are satisfied.

### 6. Model Weight URL

Required after training:

- Hugging Face, AI Studio, or Baidu Netdisk URL for the LoRA adapter/checkpoint.
- Exact base model name and version.
- Inference instructions.

### 7. Final Submission Email

Only send the final email after the following fields are real:

- GitHub repository URL
- Public dataset URL
- Model/checkpoint URL
- Technical report URL
- Demo URL or reproducible local demo instructions

If a model is not trained yet, the email must say so explicitly and should not be
presented as a completed fine-tuned model submission.
