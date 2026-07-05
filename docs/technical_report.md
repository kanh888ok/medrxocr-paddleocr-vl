# 技术报告

## 项目说明

MedRxOCR 是一个处方 OCR 评测项目。当前工作基于公开、已脱敏的数据，整理统一 JSONL 格式，固定 train/val/eval 划分，并给出 PaddleOCR-VL 系列模型的基线和 LoRA/SFT 结果。

当前数据覆盖三类任务：

- 整页处方 OCR 文本。
- 药品区域检测。
- 手写药品词识别。

药品剂量、频次、疗程等结构化字段还需要后续人工补充标注。

## 数据来源

| 数据源 | 许可证 | 用途 |
|---|---|---|
| Image-to-Text Bilingual Dataset from Medical Prescriptions | CC BY 4.0 | 整页处方 OCR |
| Bangladesh prescription YOLO dataset | CC BY 4.0 | 药品区域检测 |
| RxHandBD | CC BY 4.0 | 手写药品词识别 |

GitHub 不存放大文件。原始图片、处理后的大 JSONL、数据统计和初始检查点放在 AI Studio 或本地数据目录。当前 LoRA/SFT 指标和小结果以 GitHub 中的文档、脚本和 `outputs/` 为准。

## 数据划分

| 划分 | 数量 |
|---|---:|
| train | 4801 |
| val | 607 |
| eval | 1367 |

按来源统计：

| 数据源 | train | val | eval |
|---|---:|---:|---:|
| Mendeley bilingual | 681 | 110 | 206 |
| Bangladesh YOLO | 141 | 13 | 46 |
| RxHandBD | 3979 | 484 | 1115 |

Mendeley 原始包有 1000 张图，CSV 清洗后有 997 条可用标注。

## 质量检查

已检查图片路径、`image_id` 重复、必填字段、脱敏标记、数据来源和任务类型。当前 train/val/eval 中未发现缺图、重复 ID、必填字段缺失或未脱敏标记问题。

## 基线

RxHandBD 词图 eval 共 1115 张：

| 模型 | 图像数 | 错误数 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0 | 0.2386 | 0.4327 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0 | 0.2197 | 0.4851 | 0.4736 |

这些是零样本结果，不是微调后指标。

## 实拍评估

已补充 20 张手机实拍图的人工质检。其中 18 张对应固定 eval，可作为严格实拍评估；另 2 张对应 train，只作为采集示例。

`realshot_eval_18` 结果：

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.5 | 18 | 11 | 7 | 0.9542 | 0.9124 |
| PaddleOCR-VL v1 本地模型 | 18 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA step512 | 18 | 18 | 0 | 0.8729 | 0.8679 |

实拍评估用 warm-worker 方式运行：模型先加载并常驻，单张图片单独计时；若某张图超时，则杀掉 worker、重启并重试。

## LoRA/SFT 微调

当前微调只使用公开 RxHandBD 词图，不包含真实线下处方。

| 项目 | 数值 |
|---|---:|
| 基础训练样本 | 3979 |
| 轻增强训练样本 | 3979 原图 + 1800 增强图 |
| 评估样本 | 1115 |
| LoRA rank | 8 |
| 推理设置 | `max_new_tokens=32` |

完整 1115 张词图结果：

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2386 | 0.4327 | 0.4255 |
| LoRA step512 | 0.2682 | 0.3831 | 0.3783 |
| LoRA aug-light step512 | 0.2825 | 0.3754 | 0.3702 |

`aug-light step512` 在公开词图上最好。它对 600 张训练图做了模糊、亮度和旋转扰动，共生成 1800 张增强图。

实拍子集仍保留 `LoRA step512` 作为当前结果。`aug-light` 在 realshot 上没有提升：max64 版本 18 张都完成，但 Micro CER 为 0.9421；max128 版本有 2 张超时。

## Demo

已补充 `demo/app.py`。该 Demo 是演示原型：自带一个脱敏样例，可以预览图片、粘贴 OCR 文本、生成统一 JSON 结构，并展示当前 baseline 与 LoRA 的评估对比。页面内的本地 OCR 推理是可选项；正式指标仍使用评估脚本运行。

## 工程化改进

已将评估指标、数据加载、文本工具和错误分析拆分到 `src/medrxocr/`，并补充 `tests/` 单元测试。当前测试不依赖模型权重和数据集，可用 `python -m unittest discover -s tests` 直接运行。

## 当前不足

- 数据主要来自公开数据，真实线下处方自采数据暂未补充。
- 结构化字段人工标注还不完整。
- 实拍子集只有 18 张，每张只有 1 个实拍版本。
- 药品词典后处理还没系统做。
