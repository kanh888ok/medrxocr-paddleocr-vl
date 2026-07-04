# 数据说明

## 数据名称

MedRxOCR Train / Val / Eval

## 用途

这套数据用于处方 OCR 和相关子任务评测。当前版本主要覆盖：

- 整页处方 OCR。
- 药品区域检测。
- 手写药品词识别。

完整药品行结构化字段还需要后续人工补充。

## 数据来源

数据来源见 `docs/data_source_registry.csv`。

## 固定划分

划分由 `scripts/create_submission_splits.py` 生成，使用 `source_id:image_id` 的哈希值保证结果稳定。

| 文件 | 数量 | 说明 |
|---|---:|---|
| `data/processed/medrxocr_train.jsonl` | 4801 | 训练集 |
| `data/processed/medrxocr_val.jsonl` | 607 | 验证集 |
| `data/processed/medrxocr_eval.jsonl` | 1367 | 评估集 |

按来源统计：

| 数据源 | 训练 | 验证 | 评估 | 说明 |
|---|---:|---:|---:|---|
| `mendeley_bilingual_1000` | 681 | 110 | 206 | 整页双语处方 OCR |
| `mendeley_bd_200_yolo` | 141 | 13 | 46 | 药品区域检测 |
| `rxhandbd_5578` | 3979 | 484 | 1115 | 官方测试集保留为评估集 |

## 数据完整性

没有加入合成处方，也没有补造缺失标注。

Mendeley bilingual 原始包有 1000 张图片，但 CSV 清洗后只有 997 个唯一可用图片 ID。重复 ID：

- `0063`
- `0185`
- `0676`
- `0856`

缺少唯一 CSV 标注的图片：

- `0186`
- `0674`
- `0747`

所以本项目报告 997 条可用唯一标注。

## 原始包校验

| 文件 | SHA256 |
|---|---|
| `Prescription_Dataset_1000.zip` | `D862F6F0AF1948A442C12A789F46258F2367348F593AFCCD49DE24E304F211DF` |
| `RxHandBD-ML.zip` | `C6371C0A3A89301C0B6B2EAC1D2D49F6F3D8E559A7A71B338655DDE0A6A63B51` |
| `Dataset.zip` | `CED4394523998386B274E549469C144FA9718402B4C52764552914182BB331DB` |

## 质量检查

当前检查项：

- 图片是否存在。
- `image_id` 是否重复。
- 必填字段是否缺失。
- 脱敏标记是否为 true。
- 数据来源、难度和视觉标签分布。

预测文件只包含公开 CC BY 4.0 评测记录的标签，用于复核指标。
