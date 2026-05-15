# Risk Control

## Main Risks

### 1. Evaluation set seen as only internet-downloaded public data

Mitigation:
- Re-annotate and normalize into MedRxOCR schema.
- Add difficulty stratification.
- Add quality-audit report.
- Add multi-task evaluation, not just plain OCR.
- Use public data as legal source but contribute new benchmark protocol.

### 2. Synthetic-data disqualification

Mitigation:
- Synthetic data only in training augmentation.
- Explicitly label synthetic samples.
- Exclude synthetic data from core evaluation set.

### 3. Medical privacy risk

Mitigation:
- Use de-identified public datasets.
- Run manual and automatic PII check.
- Do not release unredacted raw prescriptions.

### 4. Weak originality

Mitigation:
- Emphasize structured prescription extraction.
- Add lexicon-constrained decoding.
- Add medicine-region detection and word-level recognition subtasks.
- Provide reproducible scripts and schema.

### 5. Weak model score

Mitigation:
- Use zero-shot baseline first.
- LoRA SFT with small subset.
- Focus scoring narrative on full benchmark contribution and reproducibility.
