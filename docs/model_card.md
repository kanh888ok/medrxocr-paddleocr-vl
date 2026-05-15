# Model Card: MedRxOCR-PaddleOCR-VL

## Base Model

- PaddleOCR-VL
- PaddleOCR-VL-1.5

## Adaptation

Current repository status:

- Zero-shot baselines are complete for the full RxHandBD word-level eval subset.
- LoRA SFT is planned but not completed.
- Multi-task instruction tuning is planned but not completed.
- JSON-structured prescription extraction is represented in the schema and data
  protocol, but a fine-tuned extractor checkpoint has not been published.
- Lexicon-constrained normalization is planned as an ablation.

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

The target fine-tuned model is expected to output structured JSON following
`schemas/medrxocr_schema.json`. The current zero-shot word-level baselines output
plain OCR text for cropped prescription-word images.

## Limitations

- Handwriting ambiguity remains difficult.
- Rare drug names require external lexicon support.
- Redacted fields cannot be recovered.
- Public datasets may not cover all domestic Chinese prescription layouts.
