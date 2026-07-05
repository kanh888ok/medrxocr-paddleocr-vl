# LoRA 后续实验

现在主结果是 `rank=8, step512`。这份文件只记录下一轮该怎么跑，不把没跑完的实验写成结果。

## 要比较什么

| 实验 | 入口 | 目的 |
|---|---|---|
| rank4 | `configs/experiments/erniekit_paddleocr_vl_lora_word_rank4_win4070.yaml` | 看更小 rank 是否够用 |
| rank16 | `configs/experiments/erniekit_paddleocr_vl_lora_word_rank16_win4070.yaml` | 看更大 rank 是否继续提升 |
| aug_rank8 | `scripts/build_augmented_word_sft_manifest.py` + `configs/experiments/erniekit_paddleocr_vl_lora_word_aug_rank8_win4070.yaml` | 用模糊、亮度、旋转、透视模拟手机拍摄 |
| hard_focus_rank8 | `scripts/build_hard_word_sft_manifest.py` + `configs/experiments/erniekit_paddleocr_vl_lora_word_hard_focus_rank8_win4070.yaml` | 从训练集里挑长词、带数字、较难样本做重点训练 |

## 运行方式

先生成配置：

```powershell
python scripts\make_lora_experiment_configs.py
```

单个实验：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_lora_strategy_matrix_win4070.ps1 -Experiment rank4
powershell -ExecutionPolicy Bypass -File scripts\run_lora_strategy_matrix_win4070.ps1 -Experiment rank16
powershell -ExecutionPolicy Bypass -File scripts\run_lora_strategy_matrix_win4070.ps1 -Experiment aug_rank8
powershell -ExecutionPolicy Bypass -File scripts\run_lora_strategy_matrix_win4070.ps1 -Experiment hard_focus_rank8
```

`aug_rank8` 会先生成增强图片和 SFT 清单；增强图片放在 `data/interim`，不进 Git。

`hard_focus_rank8` 只从训练集选样本，不会拿 eval 结果回灌训练。后面如果有训练集预测文件，可以用 `--predictions` 按训练集 CER 挑难样本。

如果本地已经有合并后的 `step512` 检查点，可以把 hard-focus 配置里的 `model_name_or_path` 改成该检查点路径，再作为二阶段继续训练。不改路径时，它只是难样本重点训练。

## 评估口径

训练完成后仍用同一套 eval：

- RxHandBD 1115 张固定 eval。
- `realshot_eval_18` 手机实拍子集。

只有完整跑完并确认没有超时后，才把新指标写进 README 和报告。
