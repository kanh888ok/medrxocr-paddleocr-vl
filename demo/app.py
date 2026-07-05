import json
import re
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "outputs" / "lora_word_eval500_comparison.json"


def load_metrics():
    if not METRICS_PATH.exists():
        return None
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def split_drug_lines(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    drug_lines = []
    keywords = ("tab", "tablet", "cap", "capsule", "mg", "ml", "胶囊", "片", "tablet", "capsule")
    for line in lines:
        low = line.lower()
        if any(key in low for key in keywords):
            drug_lines.append(line)
    return drug_lines


def build_structured_output(text):
    medications = []
    for line in split_drug_lines(text):
        cleaned = re.sub(r"^\s*(tab\.?|cap\.?)\s+", "", line, flags=re.IGNORECASE)
        name = re.split(r"\s{2,}|,|;|\t", cleaned, maxsplit=1)[0].strip()
        medications.append(
            {
                "drug_name_raw": name or line,
                "drug_name_normalized": name.lower() if name else None,
                "strength": None,
                "dose": None,
                "frequency": None,
                "route": None,
                "duration": None,
                "instruction": line,
            }
        )

    return {
        "document_type": "prescription",
        "patient": {"name": "[REDACTED]", "age": None, "sex": None, "patient_id": "[REDACTED]"},
        "visit": {"date": None, "department": None, "diagnosis": None},
        "medications": medications,
        "doctor": {"name": "[REDACTED]", "signature_present": False, "stamp_present": False},
        "regions": [],
        "full_ocr_text": text.strip(),
    }


st.set_page_config(page_title="MedRxOCR Demo", layout="wide")
st.title("MedRxOCR 处方 OCR Demo")

metrics = load_metrics()
if metrics:
    current = metrics["comparison"][-1]
    cols = st.columns(3)
    cols[0].metric("评估样本", current["n_images"])
    cols[1].metric("LoRA Exact", f"{current['lora']['exact_match_rate']:.4f}")
    cols[2].metric("LoRA Micro CER", f"{current['lora']['micro_cer']:.4f}")
    st.dataframe(
        [
            {
                "样本数": row["n_images"],
                "Baseline Exact": row["baseline"]["exact_match_rate"],
                "LoRA Exact": row["lora"]["exact_match_rate"],
                "Baseline Micro CER": row["baseline"]["micro_cer"],
                "LoRA Micro CER": row["lora"]["micro_cer"],
            }
            for row in metrics["comparison"]
        ],
        use_container_width=True,
    )

left, right = st.columns([1, 1])

with left:
    uploaded = st.file_uploader("处方图片", type=["png", "jpg", "jpeg", "webp"])
    if uploaded:
        st.image(uploaded, use_container_width=True)

with right:
    sample_text = (
        "Tab. Onium 2+2+2\n"
        "Tab. Metryour once morning noon night for three days\n"
        "Cap. Block T once morning noon night for five days"
    )
    text = st.text_area("OCR 文本", value=sample_text, height=180)
    result = build_structured_output(text)
    st.json(result)
