# LoRA 对比实验

这轮只用公开 RxHandBD 训练图，没有加入真实线下处方。

当前结论很直接：

- 公开 1115 张词图：`aug-light rank8 step512` 最好。
- 实拍 18 张：原来的 `rank8 step512` 更稳，继续作为实拍子集推荐结果。

## 选择 LoRA 的原因

本项目的数据量不大，目标是验证 PaddleOCR-VL 在处方 OCR 场景里的适配效果。直接全量微调成本高，也不适合在本机 RTX 4070 上反复试验。LoRA 只训练少量适配参数，能在较低显存下完成训练、保存适配器，并保留基础模型能力，所以先作为微调方案。

rank 选择从 8 开始。它的显存和速度比较稳，前 500 张和完整 1115 张评估都有提升。后面补了 rank4、rank16 和增强实验，用来确认是否有更好的替代方案。

## 已跑结果

| 实验 | 口径 | 结果 | 是否采用 |
|---|---|---|---|
| rank4 step512 | 先看前 4 张 | 单张约 48-62 秒，速度太慢 | 不采用 |
| rank16 step512 | 前 20 张 | Micro CER 0.2000，略差于同口径 step512 的 0.1923 | 不采用 |
| aug-rank8 step512 | 前 100 张 | Micro CER 0.7085，略差于同口径 step512 的 0.7037 | 不采用 |
| aug-light rank8 step512 | 固定 eval 1115 张 | Exact 0.2825，Mean CER 0.3754，Micro CER 0.3702 | 公开词图采用 |
| aug-light realshot max64 | 实拍 18 张 | 18/18 完成，Micro CER 0.9421 | 不采用 |
| aug-light realshot max128 | 实拍 18 张 | 16/18 完成，2 张超时，Micro CER 0.9104 | 不采用 |

## 为什么保留 rank8

| 方案 | 观察 | 结论 |
|---|---|---|
| rank4 | 单张推理约 48-62 秒 | 速度不合适，停止 |
| rank8 | 1115 张公开词图稳定提升，realshot 18 张也比基线好 | 当前主结果 |
| rank16 | 前 20 张略差于同口径 rank8 | 没继续扩大 |

rank8 不是因为参数最少，而是因为它在速度、显存和指标之间最稳。rank16 没有带来明确收益，rank4 速度太慢，所以没有继续投入完整评估。

对比主结果：

| 模型 | 数据 | Exact Match | Mean CER | Micro CER |
|---|---|---:|---:|---:|
| PaddleOCR-VL 基线 | RxHandBD eval 1115 | 0.2386 | 0.4327 | 0.4255 |
| LoRA rank8 step512 | RxHandBD eval 1115 | 0.2682 | 0.3831 | 0.3783 |
| LoRA aug-light rank8 step512 | RxHandBD eval 1115 | 0.2825 | 0.3754 | 0.3702 |

实拍子集：

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL v1 本地模型 | 18 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA rank8 step512 | 18 | 18 | 0 | 0.8729 | 0.8679 |
| LoRA aug-light rank8 max64 | 18 | 18 | 0 | 0.9293 | 0.9421 |
| LoRA aug-light rank8 max128 | 18 | 16 | 2 | 0.9146 | 0.9104 |

公开词图和实拍子集分开采用结果。`aug-light` 在公开词图上提升明显，但到了 realshot 后没有继续提升，所以只写作公开词图推荐结果；实拍子集仍保留普通 `rank8 step512`。

## aug-light 怎么做

`aug-light` 只对训练集中 600 张图做扰动，每张生成 3 个版本：

- blur：轻微模糊。
- bright：亮度/对比度变化。
- rotate：小角度旋转。

原始 3979 张训练图仍保留，所以训练清单是 5779 条。增强图放在 `data/interim`，不进 Git。

生成命令：

```powershell
python scripts\build_augmented_word_sft_manifest.py `
  --output data\processed\train_rx_erniekit_sft_word_aug_light.jsonl `
  --image-output-dir data\interim\rxhandbd_camera_aug_light `
  --summary-output outputs\lora_augmented_word_light_manifest_summary.json `
  --variants blur bright rotate `
  --augmentation-limit 600 `
  --include-original
```

训练配置：

```text
configs/experiments/erniekit_paddleocr_vl_lora_word_aug_light_rank8_win4070.yaml
```

## 还没继续的方向

- `hard_focus_rank8` 还没完整训练和评估。
- 药品词典后处理还没做系统对比。
- realshot 上目前没有比 `rank8 step512` 更好的微调版本。
- rank16/重增强说明“试过但没更好”，不建议继续优先投时间。
