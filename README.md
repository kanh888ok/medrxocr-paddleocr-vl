# MedRxOCR 处方 OCR 数据集

本项目整理了一套基于公开处方数据的 OCR 评测基准，并提供 PaddleOCR-VL 的评测脚本、数据转换脚本和训练清单生成脚本。

项目重点不是写一份很长的说明，而是把数据来源、处理方式、评测口径和结果说清楚。

## 已完成内容

- 整理 3 个公开数据源，许可证均为 CC BY 4.0。
- 将原始标注转换为统一 JSONL 格式。
- 固定训练集、验证集、评估集划分。
- 生成数据统计和质量检查结果。
- 提供 PaddleOCR-VL / PaddleOCR-VL-1.5 在 RxHandBD 词图评估集上的 zero-shot 基线。
- 提供 SFT 训练清单和 LoRA/SFT 配置文件。
- 发布一个初始检查点，便于后续继续训练和复现实验。

## 数据说明

大文件不放在 GitHub 仓库里。原始数据、处理后的 JSONL、质量检查结果放在 AI Studio 数据包：

https://aistudio.baidu.com/dataset/detail/384020/intro

初始检查点放在：

https://aistudio.baidu.com/dataset/detail/384021/intro

GitHub 只保留代码、配置、示例和文档。

## 数据来源

| 数据源 | 用途 | 数量说明 |
|---|---|---:|
| Mendeley bilingual prescription | 整页处方 OCR | 997 条可用唯一标注 |
| Bangladesh 200 prescription YOLO | 药品区域检测 | 200 张处方图 |
| RxHandBD | 手写药品词识别 | 4463 训练 / 1115 评估 |

注意：Mendeley bilingual 原始包有 1000 张图片，但 CSV 清洗后只有 997 条唯一可用标注。因此本文档按 997 条报告，不写成 1000 条完整标注。

## 处理后的划分

| 划分 | 数量 |
|---|---:|
| 训练集 | 4801 |
| 验证集 | 607 |
| 评估集 | 1367 |

## 基线结果

评测对象是 RxHandBD 的 1115 张手写词图，不是整页处方结构化抽取。

| 模型 | 图像数 | 错误数 | Exact Match | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0 | 0.2197 | 0.4736 |

这些结果是 zero-shot 基线，不是微调后指标。

## 实拍评估补充

已制作第一版实拍评估子集：20 张手机实拍图已完成原图匹配和人工质检，其中 18 张对应固定 eval 集，可用于严格实拍评估；另外 2 张对应 train 集，只作为采集示例。说明见 `docs/realshot_eval.md` 和 `docs/realshot_manual_qc.md`。

## 目录重点

- `docs/technical_report.md`：数据、质量检查和基线结果。
- `docs/realshot_eval.md`：实拍评估子集说明。
- `docs/realshot_manual_qc.md`：实拍图片人工质检结果。
- `docs/dataset_card.md`：数据来源和划分。
- `docs/model_card.md`：模型用途、限制和指标口径。
- `schemas/medrxocr_schema.json`：统一标注格式。
- `scripts/`：数据转换、质量检查、评测和训练清单生成脚本。
- `configs/`：LoRA/SFT 配置。
- `demo/`：本地 Streamlit 示例。

## 基本流程

下载数据后，将文件放到 `data/raw/`，再按下面顺序处理：

```bash
python scripts/prepare_mendeley_bilingual.py --csv data/raw/mendeley_bilingual/annotations.csv --image-root data/raw/mendeley_bilingual/images --output data/interim/mendeley_bilingual.jsonl

python scripts/prepare_rxhandbd.py --labels data/raw/rxhandbd/train_labels.csv --image-root data/raw/rxhandbd/train --split train --output data/interim/rxhandbd_train.jsonl

python scripts/prepare_rxhandbd.py --labels data/raw/rxhandbd/test_labels.csv --image-root data/raw/rxhandbd/test --split eval --output data/interim/rxhandbd_eval.jsonl

python scripts/prepare_bangladesh_yolo.py --image-root data/raw/bd200/images --label-root data/raw/bd200/labels --output data/interim/bd200_regions.jsonl

python scripts/create_submission_splits.py --mendeley data/interim/mendeley_bilingual.jsonl --rxhandbd-train data/interim/rxhandbd_train.jsonl --rxhandbd-eval data/interim/rxhandbd_eval.jsonl --bd200 data/interim/bd200_regions.jsonl --output-dir data/processed
```

生成训练清单：

```bash
python scripts/build_sft_manifest.py --input data/processed/medrxocr_train.jsonl --output data/processed/train_rx_sft.jsonl
```

## 当前不足

- 目前训练集、验证集、评估集主要来自公开数据。
- 还需要补充自行收集并人工质检的高价值处方数据。
- 初始检查点已发布，但还需要补充完整微调实验和微调后指标。
