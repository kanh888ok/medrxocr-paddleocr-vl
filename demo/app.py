import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "outputs" / "lora_eval1115_realshot_summary.json"
SAMPLE_IMAGE_PATH = ROOT / "demo" / "samples" / "sample_prescription.svg"
SAMPLE_TEXT_PATH = ROOT / "demo" / "samples" / "sample_ocr_text.txt"
STRENGTH_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:mg|g|mcg|μg|ug|ml|iu|%)\b", re.IGNORECASE)
DURATION_RE = re.compile(r"\bfor\s+([\w-]+)\s+(day|days|week|weeks)\b", re.IGNORECASE)


def load_metrics():
    if not METRICS_PATH.exists():
        return None
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def load_sample_text():
    if SAMPLE_TEXT_PATH.exists():
        return SAMPLE_TEXT_PATH.read_text(encoding="utf-8").strip()
    return ""


def flatten_strings(obj: Any) -> list[str]:
    texts: list[str] = []
    if isinstance(obj, str):
        if obj.strip():
            texts.append(obj)
    elif isinstance(obj, dict):
        for key in ("block_content", "rec_text", "text", "label"):
            value = obj.get(key)
            if isinstance(value, str) and value.strip():
                texts.append(value)
        for value in obj.values():
            if isinstance(value, (dict, list)):
                texts.extend(flatten_strings(value))
    elif isinstance(obj, list):
        for item in obj:
            texts.extend(flatten_strings(item))
    return texts


def result_text(item: Any) -> str:
    markdown = getattr(item, "markdown", None)
    if isinstance(markdown, str) and markdown.strip():
        return markdown.strip()

    data = getattr(item, "json", None)
    if isinstance(data, dict):
        blocks = data.get("res", {}).get("parsing_res_list", [])
        block_text = "\n".join(
            str(block.get("block_content", "")).strip()
            for block in blocks
            if isinstance(block, dict) and str(block.get("block_content", "")).strip()
        )
        if block_text:
            return block_text
        texts = flatten_strings(data)
        if texts:
            return "\n".join(dict.fromkeys(texts))

    return str(item).strip()


@st.cache_resource(show_spinner=False)
def load_local_ocr(pipeline_version: str, model_dir: str, disable_layout: bool):
    from paddleocr import PaddleOCRVL

    kwargs: dict[str, Any] = {"pipeline_version": pipeline_version}
    if model_dir:
        kwargs["vl_rec_model_dir"] = model_dir
    if disable_layout:
        kwargs["use_layout_detection"] = False
    return PaddleOCRVL(**kwargs)


def run_local_ocr(uploaded_file, pipeline_version: str, model_dir: str, disable_layout: bool, max_new_tokens: int) -> str:
    pipe = load_local_ocr(pipeline_version, model_dir, disable_layout)
    suffix = Path(uploaded_file.name).suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name
    try:
        kwargs: dict[str, Any] = {}
        if max_new_tokens > 0:
            kwargs["max_new_tokens"] = max_new_tokens
        items = list(pipe.predict(tmp_path, **kwargs))
        return result_text(items[0]) if items else ""
    finally:
        Path(tmp_path).unlink(missing_ok=True)


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
        name_part = STRENGTH_RE.split(cleaned, maxsplit=1)[0]
        name_part = re.split(r"\b(?:once|twice|tid|bid|qd|morning|noon|night)\b", name_part, maxsplit=1, flags=re.I)[
            0
        ]
        name = re.split(r"\s{2,}|,|;|\t", name_part, maxsplit=1)[0].strip()
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
st.title("MedRxOCR 演示原型")
st.caption("用于查看评估结果、预览图片、演示 OCR 文本到 JSON 的转换；默认不加载 PaddleOCR-VL 模型。")
if "ocr_text_value" not in st.session_state:
    st.session_state["ocr_text_value"] = load_sample_text()

metrics = load_metrics()
if metrics:
    word_eval = metrics["rxhandbd_eval1115"].get("lora_aug_light_rank8_step512") or metrics["rxhandbd_eval1115"][
        "lora_step512"
    ]
    realshot = metrics["realshot_eval18"]["lora_step512"]
    cols = st.columns(3)
    cols[0].metric("词图评估样本", word_eval["n_images"])
    cols[1].metric("词图推荐 Exact", f"{word_eval['exact_match']:.4f}")
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

with st.expander("本地 OCR 推理", expanded=False):
    enable_local_ocr = st.checkbox("启用本地 OCR", value=False)
    pipeline_version = st.selectbox("PaddleOCR-VL 版本", ["v1", "v1.5"], index=0)
    model_dir = st.text_input("模型目录", value=os.environ.get("MEDRXOCR_VL_REC_MODEL_DIR", ""))
    max_new_tokens = st.number_input("max_new_tokens", min_value=0, max_value=256, value=128, step=8)
    disable_layout = st.checkbox("关闭版面检测", value=True)
    st.caption("未勾选时 Demo 不加载模型。启用后需要本机已安装 PaddleOCR-VL，并准备好模型目录。")

left, right = st.columns([1, 1])

with left:
    image_source = st.radio("图片来源", ["内置样例", "上传图片"], horizontal=True)
    uploaded = None
    if image_source == "内置样例":
        if SAMPLE_IMAGE_PATH.exists():
            st.image(str(SAMPLE_IMAGE_PATH), use_container_width=True)
        st.caption("内置样例只用于演示流程，不是真实处方。")
        if st.button("载入样例 OCR 文本"):
            st.session_state["ocr_text_value"] = load_sample_text()
    else:
        uploaded = st.file_uploader("处方图片", type=["png", "jpg", "jpeg", "webp"])
    if uploaded:
        st.image(uploaded, use_container_width=True)
        st.caption("未启用本地 OCR 时，这里只做图片预览。真实批量评估请使用 scripts/run_paddleocrvl_*.py。")
        if enable_local_ocr and st.button("运行本地 OCR"):
            try:
                with st.spinner("正在本地推理..."):
                    st.session_state["ocr_text_value"] = run_local_ocr(
                        uploaded,
                        pipeline_version=pipeline_version,
                        model_dir=model_dir,
                        disable_layout=disable_layout,
                        max_new_tokens=int(max_new_tokens),
                    )
            except Exception as exc:
                st.error(f"本地 OCR 未运行成功：{exc}")

with right:
    text = st.text_area("OCR 文本", key="ocr_text_value", height=180)
    result = build_structured_output(text)
    st.caption("字段提取是规则原型：strength、frequency、duration 只做简单识别，dose、route 等字段仍需人工标注或后续模型支持。")
    st.json(result)
