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
- GitHub repository created and pushed:
  `https://github.com/kanh888ok/medrxocr-paddleocr-vl`.
- PaddleOCR-VL and PaddleOCR-VL-1.5 zero-shot results completed on the full
  RxHandBD word-level eval subset:
  - `outputs/paddleocrvl_v1_rxhandbd_word_eval/metrics.json`
  - `outputs/paddleocrvl_v1_rxhandbd_word_eval/predictions.jsonl`
  - `outputs/paddleocrvl_v15_rxhandbd_word_eval/metrics.json`
  - `outputs/paddleocrvl_v15_rxhandbd_word_eval/predictions.jsonl`
  - `outputs/paddleocrvl_rxhandbd_word_eval_summary.json`

## Remaining Work Before Final Submission

### 1. PaddleOCR-VL Zero-Shot

Goal: run the official PaddleOCR-VL pipeline on `data/processed/medrxocr_eval.jsonl`.

Completed output:

- `outputs/paddleocrvl_v1_rxhandbd_word_eval/predictions.jsonl`
- `outputs/paddleocrvl_v1_rxhandbd_word_eval/metrics.json`
- A result table added to `docs/technical_report.md`

Current full-eval result on `rxhandbd_5578` word-level eval:

- Images: 1115 / 1115
- Errors: 0
- Exact match: 0.2386
- Micro CER: 0.4255
- Mean latency: 0.6920 sec/image

Notes:

- This is a full evaluation for the RxHandBD cropped-word subset only.
- Do not report it as a full-page structured prescription result.
- Full-page Mendeley/Bangladesh structured evaluation remains open.

### 2. PaddleOCR-VL-1.5 Zero-Shot

Goal: run PaddleOCR-VL-1.5 on the same fixed eval split.

Current status:

- Single-image full-page smoke test completed on `rx_mendeley_bilingual_1000_0003`.
- The observed full-page smoke-test CER was `10.8082`, with severe
  repetition/garbled text.
- A 5-image full-page pilot attempt was stopped after more than 30 minutes
  without a first prediction being written.
- Full RxHandBD cropped-word eval completed successfully.

Completed word-level output:

- `outputs/paddleocrvl_v15_rxhandbd_word_eval/predictions.jsonl`
- `outputs/paddleocrvl_v15_rxhandbd_word_eval/metrics.json`
- A comparable result table in `docs/technical_report.md`

Current full-eval result on `rxhandbd_5578` word-level eval:

- Images: 1115 / 1115
- Errors: 0
- Exact match: 0.2197
- Micro CER: 0.4736
- Mean latency: 0.6428 sec/image

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

Completed:

- GitHub repository:
  `https://github.com/kanh888ok/medrxocr-paddleocr-vl`

Raw large datasets are not committed to GitHub. The repository publishes source
registry, scripts, docs, small examples, and reproducible processing
instructions.

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
