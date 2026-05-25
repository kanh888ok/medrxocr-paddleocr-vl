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
- No synthetic clinical prescriptions are included in the current released
  dataset package.
- If synthetic augmentation is added in future work, it must be explicitly
  labeled and excluded from the core evaluation set.

### 3. Medical privacy risk

Mitigation:
- Use de-identified public datasets.
- Run manual and automatic PII check.
- Do not release unredacted raw prescriptions.

### 4. Weak originality

Mitigation:
- Emphasize the unified schema and protocol for structured prescription
  extraction.
- Keep lexicon-constrained decoding as a planned extension.
- Add medicine-region detection and word-level recognition subtasks.
- Provide reproducible scripts and schema.

### 5. Weak model score

Mitigation:
- Use zero-shot baseline first.
- Release a lightweight initial LoRA/SFT derivative checkpoint.
- Focus scoring narrative on full benchmark contribution and reproducibility.
