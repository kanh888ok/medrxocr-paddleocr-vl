# Current Submission Email Draft

Subject:

PaddleOCR Derivative Model Challenge - MedRxOCR Medical Prescription Recognition - kanh888ok

Recipients:

ext_paddle_oss@baidu.com
paddleocr@baidu.com
cuicheng01@baidu.com
liujiaxuan01@baidu.com

Body:

Dear PaddleOCR Challenge Organizers,

I am submitting the MedRxOCR project for the PaddleOCR Global Derivative Model
Challenge.

Project name:

MedRxOCR: Multilingual Medical Prescription Structured Recognition with
PaddleOCR-VL

Track:

Medical prescription recognition

Team size:

1

Project summary:

MedRxOCR targets medical prescription OCR and structured information extraction
from de-identified public prescription datasets. The repository provides a
unified MedRxOCR JSON schema, data conversion scripts, quality audit scripts,
fixed train/validation/evaluation splits, PaddleOCR-VL SFT manifest generation,
PaddleOCR-VL / PaddleOCR-VL-1.5 zero-shot baselines, and a lightweight initial
LoRA/SFT derivative checkpoint for the MedRxOCR task.

Current quantitative results:

- PaddleOCR-VL zero-shot on RxHandBD word-level eval:
  - 1115 / 1115 images completed
  - 0 errors
  - Exact match: 0.2386
  - Micro CER: 0.4255
- PaddleOCR-VL-1.5 zero-shot on RxHandBD word-level eval:
  - 1115 / 1115 images completed
  - 0 errors
  - Exact match: 0.2197
  - Micro CER: 0.4736

Reporting scope:

The current quantitative results are zero-shot word-level OCR baselines on the
RxHandBD eval subset. The released checkpoint is submitted separately as an
initial domain-adapted PaddleOCR-VL derivative for prescription OCR and
structured prescription-field recognition.

Submission materials:

1. GitHub repository:

https://github.com/kanh888ok/medrxocr-paddleocr-vl

2. AI Studio dataset:

https://aistudio.baidu.com/dataset/detail/384020/intro

3. AI Studio model weights:

https://aistudio.baidu.com/dataset/detail/384021/intro

4. Technical report:

https://github.com/kanh888ok/medrxocr-paddleocr-vl/blob/main/docs/technical_report.md

5. Demo:

Local Streamlit demo instructions are included in the repository under
`demo/app.py`.

Best regards,

kanh888ok
