# Submission Completion Plan

This file records the final submitted scope and optional follow-up work for the
MedRxOCR challenge package.

## Submitted Scope

- GitHub repository:
  `https://github.com/kanh888ok/medrxocr-paddleocr-vl`
- AI Studio dataset:
  `https://aistudio.baidu.com/dataset/detail/384020/intro`
- AI Studio model weights:
  `https://aistudio.baidu.com/dataset/detail/384021/intro`
- Technical report:
  `https://github.com/kanh888ok/medrxocr-paddleocr-vl/blob/main/docs/technical_report.md`

## Completed Artifacts

- Public data sources downloaded and integrity-checked.
- Raw data normalized into MedRxOCR JSONL schema.
- Fixed train, validation, and evaluation splits created.
- SFT manifests generated:
  - `data/processed/train_rx_sft.jsonl`
  - `data/processed/val_rx_sft.jsonl`
  - `data/processed/eval_rx_sft.jsonl`
- Quality reports and dataset statistics generated in `outputs/`.
- PaddleOCR-VL and PaddleOCR-VL-1.5 zero-shot results completed on the full
  RxHandBD word-level evaluation subset.
- Lightweight initial LoRA/SFT derivative checkpoint released on AI Studio.
- Dataset card, model card, technical report, configuration files, scripts,
  and local Streamlit demo shell included in the repository.

## Reported Baselines

| Model | Subset | Images | Errors | Exact Match | Micro CER |
|---|---|---:|---:|---:|---:|
| PaddleOCR-VL | RxHandBD word-level eval | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | RxHandBD word-level eval | 1115 | 0 | 0.2197 | 0.4736 |

These metrics are zero-shot OCR baselines on cropped prescription-word images.
They are not reported as LoRA/SFT metrics or full-page structured extraction
metrics.

## Optional Future Extensions

- Full-page structured prescription benchmark expansion.
- Lexicon normalization ablation.
- Hard-case analysis by dataset source and difficulty tag.
- Additional validation of the released checkpoint on broader prescription
  layouts.
