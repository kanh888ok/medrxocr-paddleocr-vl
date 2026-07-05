import json
import re
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "outputs" / "lora_eval1115_realshot_summary.json"
STRENGTH_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:mg|g|mcg|μg|ug|ml|iu|%)\b", re.IGNORECASE)
DURATION_RE = re.compile(r"\bfor\s+([\w-]+)\s+(day|days|week|weeks)\b", re.IGNORECASE)


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


def extract_strength(line):
    match = STRENGTH_RE.search(line)
    return match.group(0) if match else None


def extract_frequency(line):
    low = line.lower()
    if "morning noon night" in low or "tid" in low:
        return "three_times_daily"
    if "twice" in low or "bid" in low:
        return "twice_daily"
    if "once" in low or "qd" in low:
        return "once_daily"
    return None


def extract_duration(line):
    match = DURATION_RE.search(line)
    return match.group(0) if match else None


def build_structured_output(text):
    medications = []
    for line in split_drug_lines(text):
        cleaned = re.sub(r"^\s*(tab\.?|cap\.?)\s+", "", line, flags=re.IGNORECASE)
        name = re.split(r"\s{2,}|,|;|\t", cleaned, maxsplit=1)[0].strip()
        medications.append(
            {
                "drug_name_raw": name or line,
                "drug_name_normalized": name.lower() if name else None,
                "strength": extract_strength(line),
                "dose": None,
                "frequency": extract_frequency(line),
                "route": None,
                "duration": extract_duration(line),
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
    word_eval = metrics["rxhandbd_eval1115"]["lora_step512"]
    realshot = metrics["realshot_eval18"]["lora_step512"]
    cols = st.columns(3)
    cols[0].metric("词图评估样本", word_eval["n_images"])
    cols[1].metric("词图 LoRA Exact", f"{word_eval['exact_match']:.4f}")
    cols[2].metric("实拍 LoRA Micro CER", f"{realshot['micro_cer']:.4f}")
    st.dataframe(
        [
            {
                "数据": "RxHandBD 词图",
                "样本数": metrics["rxhandbd_eval1115"]["baseline"]["n_images"],
                "Baseline Micro CER": metrics["rxhandbd_eval1115"]["baseline"]["micro_cer"],
                "LoRA Micro CER": word_eval["micro_cer"],
            },
            {
                "数据": "realshot_eval_18",
                "样本数": metrics["realshot_eval18"]["baseline"]["n_images"],
                "Baseline Micro CER": metrics["realshot_eval18"]["baseline"]["micro_cer"],
                "LoRA Micro CER": realshot["micro_cer"],
            },
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
    st.caption("字段提取是规则原型：strength、frequency、duration 只做简单识别，dose、route 等字段仍需人工标注或后续模型支持。")
    st.json(result)
