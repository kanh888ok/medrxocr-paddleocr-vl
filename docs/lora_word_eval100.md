# LoRA 词图评估记录

本次只使用公开 RxHandBD 词图，不使用真实线下处方。

## 固定 eval 1115 张

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2386 | 0.4327 | 0.4255 |
| LoRA step512 | 0.2682 | 0.3831 | 0.3783 |
| LoRA aug-light step512 | 0.2825 | 0.3754 | 0.3702 |

`aug-light step512` 是当前公开词图推荐结果。它在 600 张训练图上加入模糊、亮度和旋转扰动，共生成 1800 张增强图。

## `realshot_eval_18`

| 模型 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL v1 本地模型 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA step512 | 18 | 0 | 0.8729 | 0.8679 |

实拍子集仍使用 `LoRA step512` 结果。`aug-light` 在实拍 18 张上没有提升，因此不写入推荐结果。

## 其他尝试

| 实验 | 结果 |
|---|---|
| step1024 | 前 100 张较好，但后续推理不稳定 |
| rank4 | 推理太慢，不采用 |
| rank16 | 前 20 张略差，不采用 |
| 重增强 rank8 | 前 100 张略差，不采用 |
| hard-focus | 前 100 张略差，不采用 |

## 结果文件

- `outputs/lora_eval1115_realshot_summary.json`
- `outputs/lora_strategy_experiment_summary.json`
