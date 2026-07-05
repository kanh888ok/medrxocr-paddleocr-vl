# LoRA/SFT 烟测记录

## 结果

本机 RTX 4070 环境已跑通 PaddleOCR-VL 的 LoRA/SFT 小规模训练链路。

这次不是正式训练，只用于确认环境、数据格式、LoRA 参数、GPU 训练和检查点保存可以正常工作。

## 本次设置

| 项目 | 内容 |
|---|---|
| 基座模型 | PaddleOCR-VL |
| 训练方式 | LoRA |
| LoRA rank | 8 |
| 样本 | RxHandBD 中较短的公开样本 |
| 训练集 | 20 条 |
| 验证集 | 5 条 |
| 训练步数 | 2 step |
| 显卡 | RTX 4070 |

## 训练结果

| 指标 | 数值 |
|---|---:|
| step 1 loss | 3.4624 |
| step 2 loss | 0.2971 |
| train loss | 1.8798 |
| train runtime | 1.60 秒 |
| train steps/s | 1.2475 |
| 可训练参数 | 1,032,192 |
| GPU 峰值保留显存 | 约 4.18 GB |

检查点已保存到本机：

`outputs/medrxocr_lora_smoke_win4070/checkpoint_run_short_nopad_maskfix_savefix`

其中 LoRA 权重文件为：

`peft_model-00001-of-00001.safetensors`

## 需要注意

这只能写成“LoRA/SFT 训练链路已完成小规模烟测”，不能写成“微调模型指标已完成”。

正式指标还需要做两步：

1. 用更多公开训练样本跑一个稳定的小规模 LoRA 版本。
2. 用同一套 eval 和 realshot_eval_18 跑微调前后对比指标。

本次没有使用真实线下处方数据，也不依赖真实线下处方数据。
