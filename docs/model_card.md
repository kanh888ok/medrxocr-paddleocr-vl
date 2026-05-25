# Model Card: MedRxOCR-PaddleOCR-VL

## Base Model

- PaddleOCR-VL
- PaddleOCR-VL-1.5

## Adaptation

Current repository status:

- Zero-shot baselines are complete for the full RxHandBD word-level eval subset.
- A lightweight initial LoRA/SFT derivative checkpoint has been released for the
  MedRxOCR task:
  `https://aistudio.baidu.com/dataset/detail/384021/intro`.
- Multi-task instruction tuning is represented through the dataset protocol,
  SFT manifests, and configuration files.
- JSON-structured prescription extraction is represented in the schema and data
  protocol.
- Lexicon-constrained normalization and broader full-page ablations are kept as
  future extensions.

Current zero-shot metrics:

| Model | Subset | Images | Errors | Exact Match | Micro CER |
|---|---|---:|---:|---:|---:|
| PaddleOCR-VL | RxHandBD word-level eval | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | RxHandBD word-level eval | 1115 | 0 | 0.2197 | 0.4736 |

## Intended Use

- Research benchmark for prescription OCR.
- Human-in-the-loop medical document digitization.
- Pharmacy workflow prototyping.

## Not Intended For

- Autonomous medical decision-making.
- Direct clinical deployment without review.
- Prescription verification without pharmacist/clinician oversight.

## Outputs

The target structured output follows `schemas/medrxocr_schema.json`. The
released checkpoint is provided as an initial domain-adapted PaddleOCR-VL
derivative for prescription OCR and structured prescription-field extraction.
The reported quantitative table above remains a zero-shot word-level baseline,
not a LoRA/SFT metric table.

## Limitations

- Handwriting ambiguity remains difficult.
- Rare drug names require external lexicon support.
- Redacted fields cannot be recovered.
- Public datasets may not cover all domestic Chinese prescription layouts.
