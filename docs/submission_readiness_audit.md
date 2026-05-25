# Submission Readiness Audit

Last updated: 2026-05-25

## Current Verdict

The repository is ready for challenge review as the MedRxOCR PaddleOCR-VL
derivative project for medical prescription OCR and structured
prescription-field recognition.

## Public Materials

- GitHub repository:
  `https://github.com/kanh888ok/medrxocr-paddleocr-vl`
- AI Studio dataset:
  `https://aistudio.baidu.com/dataset/detail/384020/intro`
- AI Studio model weights:
  `https://aistudio.baidu.com/dataset/detail/384021/intro`
- Technical report:
  `https://github.com/kanh888ok/medrxocr-paddleocr-vl/blob/main/docs/technical_report.md`

## Completed Components

- Data acquisition and integrity documentation.
- Unified MedRxOCR JSONL schema.
- Fixed train, validation, and evaluation splits.
- Quality audit and dataset statistics reports.
- PaddleOCR-VL-style SFT manifests.
- ERNIEKit PaddleOCR-VL SFT manifest builder:
  `scripts/build_erniekit_vl_sft_manifest.py`
- LoRA/SFT configuration:
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
- Lightweight initial LoRA/SFT derivative checkpoint released on AI Studio.

## Reporting Scope

The quantitative results in this repository are reported as RxHandBD
word-level zero-shot OCR baselines. They are not reported as LoRA/SFT metrics or
as full-page structured prescription extraction metrics.

The released checkpoint is submitted as an initial domain-adapted
PaddleOCR-VL derivative for prescription OCR and structured prescription-field
recognition. It is intended for research evaluation in the challenge setting,
not direct clinical deployment.

## Optional Future Extensions

- Larger full-page structured prescription benchmarks.
- Additional ablation studies.
- Hard-case breakdowns by source, difficulty, and task type.
- Lexicon-constrained normalization experiments.
