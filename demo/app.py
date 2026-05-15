import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="MedRxOCR Demo", layout="wide")
st.title("MedRxOCR: Medical Prescription Structured Recognition Demo")

st.markdown("""
This is a local demo shell for the competition repository.
Replace the placeholder prediction function with PaddleOCR-VL inference after model setup.
""")

uploaded = st.file_uploader("Upload a prescription image", type=["png", "jpg", "jpeg", "webp"])

def placeholder_predict():
    return {
        "document_type": "prescription",
        "patient": {"name": "[REDACTED]", "age": None, "sex": None, "patient_id": "[REDACTED]"},
        "visit": {"date": None, "department": None, "diagnosis": None},
        "medications": [
            {
                "drug_name_raw": "[UNK]",
                "drug_name_normalized": "[UNK]",
                "strength": None,
                "dose": None,
                "frequency": None,
                "route": None,
                "duration": None,
                "instruction": None
            }
        ],
        "doctor": {"name": "[REDACTED]", "signature_present": False, "stamp_present": False},
        "regions": [],
        "full_ocr_text": "[PLACEHOLDER: connect PaddleOCR-VL inference here]"
    }

if uploaded:
    st.image(uploaded, caption="Input prescription", use_container_width=True)
    pred = placeholder_predict()
    st.subheader("Structured Output JSON")
    st.json(pred)
