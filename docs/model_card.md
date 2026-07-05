# 模型说明

## 基础模型

- PaddleOCR-VL
- PaddleOCR-VL-1.5

## 当前状态

- 已完成 RxHandBD 词图评估集的 zero-shot 基线。
- 已发布初始检查点：`https://aistudio.baidu.com/dataset/detail/384021/intro`。
- 已提供 SFT 清单生成脚本和 LoRA/SFT 配置。
- 已完成 1115 张公开词图的 LoRA/SFT 微调后指标。
- 已完成 `realshot_eval_18` 的微调前后对比。

## 基线结果

| 模型 | 数据集 | 图像数 | 错误数 | Exact Match | Micro CER |
|---|---|---:|---:|---:|---:|
| PaddleOCR-VL | RxHandBD 词图评估集 | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | RxHandBD 词图评估集 | 1115 | 0 | 0.2197 | 0.4736 |

这些结果是 zero-shot 词图识别结果，不是 LoRA/SFT 微调结果，也不是整页处方结构化抽取结果。

## LoRA/SFT 结果

完整 1115 张公开 RxHandBD 词图：

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2386 | 0.4327 | 0.4255 |
| LoRA step512 | 0.2682 | 0.3831 | 0.3783 |
| LoRA aug-light step512 | 0.2825 | 0.3754 | 0.3702 |

`realshot_eval_18` 实拍子集：

| 模型 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL v1 本地模型 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA step512 | 18 | 0 | 0.8729 | 0.8679 |

公开词图推荐使用 `aug-light step512` 结果；实拍子集仍使用 `LoRA step512` 结果。该结果只说明公开词图 OCR 和小规模实拍子集上有提升，不能替代完整处方结构化评估。

## 适用场景

- 处方 OCR 评测。
- 医疗文档数字化原型验证。
- 人工审核辅助流程。

## 不适用场景

- 自动医疗决策。
- 无人工审核的临床使用。
- 直接用于处方真实性判断。

## 输出格式

结构化输出格式见：

```text
schemas/medrxocr_schema.json
```

当前公开标注主要覆盖 OCR 文本、药品区域框和手写词识别。更细的药品名、剂量、频次、疗程等字段还需要人工补充。

## 限制

- 手写模糊和拍照质量差时错误较多。
- 罕见药品名需要词典辅助。
- 已脱敏字段不能恢复。
- 公开数据不能代表所有中文处方版式。
