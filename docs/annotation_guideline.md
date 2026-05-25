# MedRxOCR Annotation Guideline

## 1. Annotation Goal

Convert prescription images into a structured JSON annotation format. Do not
infer invisible content. Use `[UNK]` for unreadable text and `null` for missing
fields.

The current released labels mainly cover full-page OCR text, medicine-region
detection, and word-level prescription OCR. The schema also provides a protocol
for future structured prescription-field extraction.

## 2. Output Schema

Annotation JSON core fields:

- document_type
- patient
- visit
- medications
- doctor
- full_ocr_text
- regions

Sample-level metadata fields:

- visual_tags
- difficulty
- language
- source_id
- license
- pii_redacted

## 3. Medication Line Fields

Each medication line may contain:

```json
{
  "drug_name_raw": "",
  "drug_name_normalized": "",
  "strength": "",
  "dose": "",
  "frequency": "",
  "route": "",
  "duration": "",
  "instruction": ""
}
```

## 4. Annotation Rules

### Raw Fields

- Keep `*_raw` fields faithful to the image text.
- Do not expand abbreviations or silently correct spelling in raw fields.

### Normalized Fields

- Use normalized fields for standardized spelling, units, frequency, route, and
  drug-name normalization when reliable evidence is available.
- RxNorm, NMPA, or other drug lexicons may support future normalization work, but
  lexicon-constrained decoding is not reported as a completed benchmark in the
  current submission.

### Privacy Fields

The following content must be redacted or marked unavailable when it can identify
a person:

- patient name
- phone number
- identity number or patient ID
- address
- QR code or barcode
- doctor registration number
- doctor signature if it is personally identifying

## 5. Difficulty Tags

### easy

- clear scan or photo
- mostly printed text
- no obvious occlusion

### medium

- some handwriting
- stamp or mild skew
- light blur

### hard

At least one of the following:

- heavy handwriting
- stamp or signature overlap
- strong perspective distortion
- low light or strong shadow
- fold, occlusion, correction, or crossed-out text
- rare or heavily abbreviated medicine names

## 6. visual_tags

Multiple tags may be used:

- handwritten
- printed
- mixed_printed_handwritten
- bangla
- english
- mixed_language
- blur
- skew
- perspective
- shadow
- stamp_overlap
- signature_overlap
- fold
- wrinkle
- occlusion
- crossed_out
- low_resolution
- table_like_layout
