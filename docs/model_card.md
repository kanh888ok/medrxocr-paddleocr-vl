# Model Card: MedRxOCR-PaddleOCR-VL

## Base Model

- PaddleOCR-VL
- PaddleOCR-VL-1.5

## Adaptation

- LoRA SFT
- Multi-task instruction tuning
- JSON-structured prescription extraction
- Lexicon-constrained normalization

## Intended Use

- Research benchmark for prescription OCR.
- Human-in-the-loop medical document digitization.
- Pharmacy workflow prototyping.

## Not Intended For

- Autonomous medical decision-making.
- Direct clinical deployment without review.
- Prescription verification without pharmacist/clinician oversight.

## Outputs

The model outputs structured JSON following `schemas/medrxocr_schema.json`.

## Limitations

- Handwriting ambiguity remains difficult.
- Rare drug names require external lexicon support.
- Redacted fields cannot be recovered.
- Public datasets may not cover all domestic Chinese prescription layouts.
