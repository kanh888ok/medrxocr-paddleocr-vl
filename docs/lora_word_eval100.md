# LoRA 词图评估记录

## 目的

补充基于 PaddleOCR-VL 的微调后指标，回应“需要微调并报告指标”的意见。

本次只使用公开 RxHandBD 词图，不使用真实线下处方。

## 设置

| 项目 | 内容 |
|---|---|
| 基础模型 | PaddleOCR-VL |
| 微调方式 | LoRA/SFT |
| LoRA rank | 8 |
| 训练数据 | RxHandBD 公开训练词图 3979 张 |
| 推荐检查点 | step512 |
| 评估数据 | 固定 eval 前 500 张词图 |
| 推理设置 | `max_new_tokens=32` |
| 设备 | RTX 4070 |

## 100 张结果

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.1200 | 0.7525 | 0.7246 |
| LoRA step512 | 0.1600 | 0.7359 | 0.7037 |
| LoRA step1024 | 0.2100 | 0.7280 | 0.6957 |

`step1024` 在前 100 张上最好，但继续评估时出现生成结束不稳定，部分样本耗时明显变长。

## 300 张结果

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.1733 | 0.5357 | 0.5214 |
| LoRA step512 | 0.2067 | 0.5186 | 0.5012 |

## 500 张结果

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2520 | 0.4373 | 0.4271 |
| LoRA step512 | 0.2960 | 0.4059 | 0.3954 |

`step512` 在 100、300、400、500 张固定公开词图切片上都超过基线，因此当前推荐使用 `step512` 作为小规模微调结果。

## 说明

- 这是公开词图任务的结果，不等同于完整处方结构化抽取结果。
- 完整 1115 张 eval 还没有跑完。
- realshot_eval_18 的微调前后对比还没有跑。
- `step1024` 暂不作为推荐结果，因为后续样本推理速度不稳定。

## 结果文件

- `outputs/paddleocrvl_v1_local_rxhandbd_word_eval300_max32/metrics.json`
- `outputs/paddleocrvl_lora_word_full_lr2e5_step512_rxhandbd_eval300_max32/metrics.json`
- `outputs/lora_word_eval500_comparison.json`
- `outputs/paddleocrvl_lora_word_full_lr2e5_step1024_rxhandbd_eval100_max32/metrics.json`
