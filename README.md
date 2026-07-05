# MedRxOCR 处方 OCR 数据集

本项目整理公开处方数据，建立一个基于 PaddleOCR-VL 的处方 OCR 评测基准。

仓库只放代码、配置、说明和小型结果文件。原始图片、处理后的大 JSONL、模型权重和检查点放在 AI Studio 数据包中。

- 数据包：https://aistudio.baidu.com/dataset/detail/384020/intro
- 初始检查点：https://aistudio.baidu.com/dataset/detail/384021/intro

## 已完成

- 整理 3 个公开数据源，许可证均为 CC BY 4.0。
- 生成统一 JSONL、固定 train/val/eval 划分。
- 完成数据统计和质量检查。
- 补充 PaddleOCR-VL / PaddleOCR-VL-1.5 零样本基线。
- 补充 20 张手机实拍图片人工质检，其中 18 张可计入严格 eval。
- 完成 PaddleOCR-VL-1.5 在 realshot_eval_18 上的零样本基线。
- 完成 RTX 4070 上的 LoRA/SFT 训练、合并和评估链路，并补充 500 张公开词图的微调前后对比。
- 补充本地 Streamlit Demo，用于展示图片输入、结构化 JSON 输出和当前评估结果。
- 补充评估指标模块、错误分析脚本、单元测试和轻量 CI。

## 数据来源

| 数据源 | 用途 | 数量说明 |
|---|---|---:|
| Mendeley bilingual prescription | 整页处方 OCR | 997 条可用标注 |
| Bangladesh 200 prescription YOLO | 药品区域检测 | 200 张处方图 |
| RxHandBD | 手写药品词识别 | 4463 训练 / 1115 评估 |

Mendeley 原始包有 1000 张图片，但 CSV 清洗后只有 997 条唯一可用标注，所以按 997 条报告。

## 数据划分

| 划分 | 数量 |
|---|---:|
| train | 4801 |
| val | 607 |
| eval | 1367 |

## 零样本基线

RxHandBD 词图评估集：

| 模型 | 图像数 | Exact Match | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0.2197 | 0.4736 |

realshot_eval_18 手机实拍子集：

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.5 | 18 | 11 | 7 | 0.9542 | 0.9124 |

这些是零样本基线，不是微调后指标。

## LoRA/SFT 小规模微调

已在本机 RTX 4070 上完成公开 RxHandBD 词图 LoRA/SFT 训练。当前推荐记录的是 `step512` 检查点：训练使用 3979 张公开 RxHandBD 训练词图，评估使用固定 eval 前 500 张词图。

| 项目 | 数值 |
|---|---:|
| LoRA rank | 8 |
| 可训练参数 | 1,032,192 |
| 训练步数 | 512 step |
| 训练集 | 3979 张公开 RxHandBD 词图 |
| 评估集 | 固定 eval 前 500 张 |
| 推理设置 | `max_new_tokens=32` |
| train loss | 2.8878 |
| GPU 峰值保留显存 | 约 5.76 GB |

500 张词图评估结果：

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2520 | 0.4373 | 0.4271 |
| LoRA step512 | 0.2960 | 0.4059 | 0.3954 |

结论：在固定 500 张公开词图上，`step512` 的三项指标均超过同口径基线。`step1024` 在前 100 张上更高，但在后续样本上生成速度不稳定，因此暂不作为推荐检查点。完整 eval 和 realshot_eval_18 的微调前后对比仍需继续跑。

早期 2 step 烟测说明见 `docs/lora_sft_smoke_win4070.md`。

## Demo

本地 Demo 可用于展示项目流程和结构化输出格式：

```powershell
streamlit run demo\app.py
```

说明见 `docs/demo.md`。

## 错误分析和测试

已补充错误分析脚本和基础单元测试：

```powershell
python -m unittest discover -s tests
python scripts\analyze_word_eval.py --predictions <predictions.jsonl> --output-json outputs\error_analysis.json
```

当前 LoRA step512 的 500 张词图分析：平均推理耗时 1.31s，P95 为 1.97s，无超过 10s 的慢样本。realshot_eval_18 仍有 7/18 超时，是后续重点。

## 重要文件

- `docs/technical_report.md`：数据、质检和基线结果。
- `docs/realshot_eval.md`：实拍评估子集说明。
- `docs/realshot_manual_qc.md`：实拍图片人工质检表。
- `docs/realshot_baseline.md`：实拍子集零样本基线。
- `docs/lora_sft_readiness.md`：LoRA/SFT 当前状态。
- `docs/lora_sft_smoke_win4070.md`：本机 LoRA/SFT 烟测记录。
- `docs/lora_word_eval100.md`：词图 LoRA 微调评估记录，含 100/300/400/500 张结果。
- `docs/demo.md`：本地 Demo 说明。
- `docs/engineering_improvements.md`：工程化、错误分析和测试说明。
- `docs/error_analysis_lora_eval500.md`：LoRA 500 张错误分析。
- `docs/error_analysis_realshot_eval18.md`：实拍子集超时与错误分析。
- `scripts/`：数据转换、质检、评估和训练脚本。
- `configs/`：训练配置。

## 复现提示

训练前需要先准备公开数据、`data/processed` 清单、PaddleOCR-VL 权重和 ERNIEKit 环境。

Windows 本机烟测可参考：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\apply_erniekit_windows_compat.ps1
powershell -ExecutionPolicy Bypass -File scripts\run_lora_sft_smoke_win4070.ps1
```

官方更推荐 Linux/Docker CUDA 环境。Windows 结果用于说明本机链路已经跑通。

## 当前不足

- 训练集、评估集主要来自公开数据。
- 真实线下处方数据暂未补充，后续可以用合规公开渠道继续扩展。
- 已有 500 张公开词图的微调前后对比，完整 eval 仍未跑完。
- realshot_eval_18 上的微调前后对比仍未完成。
- 实拍子集目前只有 18 张严格 eval 图片，且每张只有 1 个实拍版本。
