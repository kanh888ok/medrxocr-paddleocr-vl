# LoRA/SFT 状态

## 结论

LoRA/SFT 训练链路已经跑通：本机 RTX 4070 可以完成训练、保存适配器、合并为推理模型，并跑出固定评估指标。

公开 RxHandBD 词图推荐结果是 `aug-light rank8 step512`。实拍子集推荐结果仍是原 `rank8 step512`。

## 训练设置

| 项目 | 数值 |
|---|---:|
| 基础模型 | PaddleOCR-VL |
| 数据 | RxHandBD 公开词图 |
| 基础训练样本 | 3979 |
| 轻增强训练样本 | 3979 原图 + 1800 增强图 |
| LoRA rank | 8 |
| 推理设置 | `max_new_tokens=32` |

## 评估结果

完整 1115 张词图：

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2386 | 0.4327 | 0.4255 |
| LoRA step512 | 0.2682 | 0.3831 | 0.3783 |
| LoRA aug-light step512 | 0.2825 | 0.3754 | 0.3702 |

`realshot_eval_18`：

| 模型 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL v1 本地模型 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA step512 | 18 | 0 | 0.8729 | 0.8679 |

`aug-light` 在公开词图上提升，但在 realshot 上没有提升，因此不作为实拍推荐结果。

## 还没做

- 真实线下处方数据暂未补充。
- 结构化字段人工标注还不完整。
- 药品词典后处理还没系统做。
