# MedRxOCR Competition Execution Pack

## 项目定位

**MedRxOCR: Multilingual Medical Prescription Structured Recognition with PaddleOCR-VL**

这不是普通 OCR 项目，而是面向真实医疗处方的 **OCR + KIE + 药品行解析 + 药品字段标准化** 衍生模型项目。

核心目标：

1. 构建可复现的医疗处方识别评估协议。
2. 提供 PaddleOCR-VL / PaddleOCR-VL-1.5 zero-shot baseline，并发布 lightweight initial LoRA/SFT derivative checkpoint。
3. 输出结构化 JSON，而不是只输出纯文本。
4. 提供数据来源登记、标注规范、质控脚本、评估脚本和本地 Streamlit demo shell。
5. 合规使用公开许可数据，不伪造真实临床处方。

## 最重要的策略

官方评分里，模型微调只有 10 分；评估集、训练集、任务复杂度、文档开源合计 90 分。
因此本项目优先把“数据集与评测基准”做扎实，再做模型微调。

## 目录结构

```text
MedRxOCR_competition_execution_pack/
  README.md
  docs/
    data_source_registry.csv
    data_acquisition_plan.md
    scoring_mapping.md
    annotation_guideline.md
    dataset_card.md
    model_card.md
    submission_checklist.md
    github_progress_post.md
    submission_email_template.md
    risk_control.md
  schemas/
    medrxocr_schema.json
  scripts/
    prepare_mendeley_bilingual.py
    prepare_rxhandbd.py
    prepare_bangladesh_yolo.py
    build_sft_manifest.py
    evaluate_rxocr.py
    quality_audit.py
    dataset_stats.py
  configs/
    paddleocr_vl_lora_rx.yaml
  demo/
    app.py
  examples/
    sample_annotation.json
    sample_prediction.json
```

Current public materials:

- GitHub: https://github.com/kanh888ok/medrxocr-paddleocr-vl
- AI Studio Dataset: https://aistudio.baidu.com/dataset/detail/384020/intro
- AI Studio Model Weights: https://aistudio.baidu.com/dataset/detail/384021/intro
- Technical Report: https://github.com/kanh888ok/medrxocr-paddleocr-vl/blob/main/docs/technical_report.md

Data availability note:

Large raw, interim, and processed data files are not tracked in GitHub. They are
released through the AI Studio dataset package. After downloading the AI Studio
dataset, place or copy the processed JSONL files under `data/processed/` before
running evaluation or SFT manifest scripts.

## 推荐执行顺序

### Step 1. 下载数据

按 `docs/data_acquisition_plan.md` 里的 P0 数据源下载：

1. Mendeley 1000 张双语处方。
2. Mendeley 200 张 Bangladesh 处方 + YOLO 药品框。
3. RxHandBD 5578 个处方手写词图。

注意：Mendeley bilingual 源数据包含 1000 张图片，但 CSV 清洗后只有 997 条唯一可用标注；不要把它报告为 1000 条完整结构化标注。

### Step 2. 转换为统一 schema

```bash
python scripts/prepare_mendeley_bilingual.py --csv data/raw/mendeley_bilingual/annotations.csv --image-root data/raw/mendeley_bilingual/images --output data/interim/mendeley_bilingual.jsonl

python scripts/prepare_rxhandbd.py --labels data/raw/rxhandbd/train_labels.csv --image-root data/raw/rxhandbd/train --split train --output data/interim/rxhandbd_train.jsonl

python scripts/prepare_rxhandbd.py --labels data/raw/rxhandbd/test_labels.csv --image-root data/raw/rxhandbd/test --split eval --output data/interim/rxhandbd_eval.jsonl
```

### Step 3. 质控

```bash
python scripts/quality_audit.py --annotations data/interim/mendeley_bilingual.jsonl --root .
python scripts/dataset_stats.py --annotations data/interim/mendeley_bilingual.jsonl --output outputs/dataset_stats.json
```

### Step 4. 构建 SFT 文件

```bash
python scripts/create_submission_splits.py --mendeley data/interim/mendeley_bilingual.jsonl --rxhandbd-train data/interim/rxhandbd_train.jsonl --rxhandbd-eval data/interim/rxhandbd_eval.jsonl --bd200 data/interim/bd200_regions.jsonl --output-dir data/processed

python scripts/build_sft_manifest.py --input data/processed/medrxocr_train.jsonl --output data/processed/train_rx_sft.jsonl
python scripts/build_sft_manifest.py --input data/processed/medrxocr_val.jsonl --output data/processed/val_rx_sft.jsonl
python scripts/build_sft_manifest.py --input data/processed/medrxocr_eval.jsonl --output data/processed/eval_rx_sft.jsonl
```

### Step 5. 跑 baseline / 使用发布的 lightweight checkpoint

先跑 PaddleOCR-VL zero-shot baseline，再使用发布的 lightweight initial LoRA/SFT
derivative checkpoint 或配置文件进行后续实验。配置文件在：

```text
configs/paddleocr_vl_lora_rx.yaml
```

### Step 6. 提交

按 `docs/submission_checklist.md` 和 `docs/submission_email_template.md` 准备材料。
