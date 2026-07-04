# 技术报告

## 项目说明

MedRxOCR 是一个处方 OCR 评测项目。当前工作基于公开处方数据，整理统一格式、固定划分，并给出 PaddleOCR-VL 的基线结果。

当前标注主要覆盖三类任务：

- 整页处方 OCR 文本。
- 药品区域检测。
- 手写药品词识别。

完整的药品行结构化抽取、剂量/频次/疗程字段标注，还需要后续人工补充。

## 公开材料

- GitHub: `https://github.com/kanh888ok/medrxocr-paddleocr-vl`
- AI Studio 数据包: `https://aistudio.baidu.com/dataset/detail/384020/intro`
- 初始检查点: `https://aistudio.baidu.com/dataset/detail/384021/intro`

GitHub 不存放大文件。原始数据、处理后的 JSONL、质量检查结果和预测结果放在 AI Studio 数据包。

## 数据来源

| 数据源 | 版本 | 许可证 | 用途 |
|---|---:|---|---|
| Image-to-Text Bilingual Dataset from Medical Prescriptions | 2 | CC BY 4.0 | 整页处方 OCR |
| A Curated Bangladesh-Based Dataset of Handwritten and Printed Prescription Images | 2 | CC BY 4.0 | 药品区域检测 |
| RxHandBD | 3 | CC BY 4.0 | 手写药品词识别 |

## 数据清洗说明

项目不补造缺失标注，也不生成虚假处方。

Mendeley bilingual 原始包有 1000 张图片。CSV 中有 1001 行图片记录，但文件名归一化后只有 997 个唯一图片 ID。重复 ID 为：

- `0063`
- `0185`
- `0676`
- `0856`

缺少唯一 CSV 标注的图片为：

- `0186`
- `0674`
- `0747`

因此本项目按 997 条可用唯一标注报告，不写成 1000 条完整标注。

## 数据划分

固定划分由 `scripts/create_submission_splits.py` 生成。

| 划分 | 数量 |
|---|---:|
| 训练集 | 4801 |
| 验证集 | 607 |
| 评估集 | 1367 |

按来源统计：

| 数据源 | 训练 | 验证 | 评估 |
|---|---:|---:|---:|
| `mendeley_bilingual_1000` | 681 | 110 | 206 |
| `mendeley_bd_200_yolo` | 141 | 13 | 46 |
| `rxhandbd_5578` | 3979 | 484 | 1115 |

## 质量检查

当前 JSONL 文件已做以下检查：

- 图片路径是否存在。
- `image_id` 是否重复。
- 必填字段是否缺失。
- 是否标记为已脱敏。
- 数据来源、难度、视觉标签分布。

检查结果显示：

- 重复 ID：0。
- 缺失图片：0。
- 缺少必填字段：0。
- 未脱敏标记：0。

## 训练清单

项目提供 SFT 清单生成脚本：

```bash
python scripts/build_sft_manifest.py --input data/processed/medrxocr_train.jsonl --output data/processed/train_rx_sft.jsonl
```

ERNIEKit 格式清单：

```bash
python scripts/build_erniekit_vl_sft_manifest.py --input data/processed/medrxocr_train.jsonl --output data/processed/train_rx_erniekit_sft.jsonl
```

LoRA/SFT 配置文件：

```text
configs/erniekit_paddleocr_vl_lora_medrxocr.yaml
```

## 基线评测

当前报告的是 RxHandBD 词图评估集上的零样本结果。评估集共 1115 张图片，每张图是一个手写处方词，不是整页处方。

运行示例：

```bash
python scripts/run_paddleocrvl_word_eval.py \
  --root . \
  --input data/processed/medrxocr_eval.jsonl \
  --output-dir outputs/paddleocrvl_v1_rxhandbd_word_eval \
  --source-id rxhandbd_5578 \
  --task-type word_ocr \
  --pipeline-version v1 \
  --disable-layout
```

| 模型 | 图像数 | 错误数 | Exact Match | Mean CER | Micro CER | 秒/图 |
|---|---:|---:|---:|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0 | 0.2386 | 0.4327 | 0.4255 | 0.6920 |
| PaddleOCR-VL-1.5 | 1115 | 0 | 0.2197 | 0.4851 | 0.4736 | 0.6428 |

这些数字只作为零样本基线，不作为微调后结果。

## 实拍评估基线

为补充真实拍摄场景，项目从固定 eval 集中匹配出 18 张处方图片进行手机实拍。实拍后不重新标注，沿用原图标注，仅替换图像输入。

本次补充 PaddleOCR-VL-1.5 在 `realshot_eval_18` 上的零样本基线。运行时使用 RTX 4070 Laptop GPU，单张超时阈值为 120 秒。

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER（成功样本） | Micro CER（成功样本） |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.5 | 18 | 11 | 7 | 0.9542 | 0.9124 |

超时样本不计入 CER 均值，需单独报告。该结果说明 PaddleOCR-VL-1.5 可以运行，但实拍处方场景下零样本效果较弱，后续仍需要图像预处理和 LoRA/SFT 微调。

## 初始检查点

项目发布了一个初始检查点：

`https://aistudio.baidu.com/dataset/detail/384021/intro`

它用于后续训练和复现实验，不代表已经完成完整微调评估。微调后指标需要在固定评估集上另行报告。

## 当前不足

- 数据主要来自公开数据，还缺少自行收集并人工质检的数据。
- 药品行结构化字段标注不够完整。
- 已有初始检查点，但还需要补充正式 LoRA/SFT 训练记录和微调后指标。
- 需要增加按数据来源、难度、书写质量的错误分析。
