# Submission Readiness Audit

Last updated: 2026-05-15

## Current Verdict

The repository can be submitted as a truthful data/evaluation protocol with
PaddleOCR-VL zero-shot baselines. It should not yet be submitted as a completed
fine-tuned derivative model.

## Completed

- GitHub repository:
  `https://github.com/kanh888ok/medrxocr-paddleocr-vl`
- AI Studio dataset:
  `https://aistudio.baidu.com/dataset/detail/384002/intro`
- Data acquisition and integrity documentation.
- Unified MedRxOCR JSONL schema.
- Fixed train/validation/evaluation split.
- Quality audit and dataset statistics reports.
- SFT manifests in the original messages-style format.
- ERNIEKit PaddleOCR-VL SFT manifest builder:
  `scripts/build_erniekit_vl_sft_manifest.py`
- ERNIEKit LoRA config draft:
  `configs/erniekit_paddleocr_vl_lora_medrxocr.yaml`
- PaddleOCR-VL zero-shot full RxHandBD word-level eval:
  - 1115 / 1115 images
  - 0 errors
  - Exact match: 0.2386
  - Micro CER: 0.4255
- PaddleOCR-VL-1.5 zero-shot full RxHandBD word-level eval:
  - 1115 / 1115 images
  - 0 errors
  - Exact match: 0.2197
  - Micro CER: 0.4736

## Still Missing

### 1. LoRA SFT Training

Status: blocked by training environment.

The remote GPU has PaddleOCR inference working, but does not currently have:

- ERNIEKit
- PaddleNLP
- VisualDL

An attempted `git clone https://github.com/PaddlePaddle/ERNIE.git` on the
remote GPU timed out on GitHub port 443. The prepared SFT manifests are ready,
but the official training framework is not installed yet.

Needed to continue:

- A GPU environment that can install ERNIEKit/PaddleNLP, preferably AI Studio,
  or
- A domestic mirror / uploaded archive of the official ERNIE repository, or
- Permission to use another model-host/training route that can publish a real
  checkpoint.

### 2. Model Weight URL

Status: unavailable until LoRA SFT finishes.

Needed:

- Hugging Face, AI Studio, or Baidu Netdisk location for the trained adapter or
  checkpoint.

### 3. Public Dataset URL

Status: dataset page created; uploaded file contents still need final checking.

Dataset URL:

- `https://aistudio.baidu.com/dataset/detail/384002/intro`

Recommended upload contents:

- `data/processed/*.jsonl`
- `data/interim/*.jsonl`
- `outputs/quality_report_*.json`
- `outputs/dataset_stats_*.json`
- `outputs/paddleocrvl_*_rxhandbd_word_eval/*`
- `docs/data_source_registry.*`
- Raw archive SHA256 checksums

Do not claim raw images are hosted unless they are actually uploaded or linked
back to the original Mendeley pages.

### 4. Final Technical Report

Status: Markdown report exists; final PDF/export still needed if the submission
expects a formal report artifact.

Current report:

- `docs/technical_report.md`

Needed:

- Final PDF or public report URL.

### 5. Full-Page Structured Benchmark

Status: not completed.

PaddleOCR-VL-1.5 full-page smoke test on one Mendeley prescription completed,
but produced severe repetition and poor CER. The 5-image full-page pilot was too
slow and was stopped. The current reliable full results are word-level RxHandBD
only.

## User-Required Items

These cannot be completed locally without user-provided access or links:

- Model checkpoint hosting destination after training.
- A training environment with ERNIEKit install access, or a domestic mirror /
  uploaded ERNIEKit package.
- Final submission preference: send now as a baseline/protocol project, or wait
  for LoRA SFT.

## Safe Submission Wording

Use this wording if submitting before LoRA SFT:

> MedRxOCR currently provides a reproducible medical prescription OCR/KIE data
> protocol, fixed train/validation/evaluation splits, quality audit scripts, and
> PaddleOCR-VL / PaddleOCR-VL-1.5 zero-shot baselines on the full RxHandBD
> word-level evaluation subset. LoRA SFT training and checkpoint publication are
> prepared but not yet completed.

Do not write:

- "LoRA SFT completed"
- "fine-tuned model checkpoint available"
- "full MedRxOCR structured benchmark completed"
- "Mendeley bilingual has 1000 unique usable annotations"
