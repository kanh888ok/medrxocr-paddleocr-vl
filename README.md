# MedRxOCR 处方 OCR 数据集

这个仓库整理了几份公开处方数据，用来做 PaddleOCR-VL 的处方 OCR 评测和小规模 LoRA/SFT 实验。

代码、配置、评估脚本和当前指标放在 GitHub。原始图片、大 JSONL、数据统计和初始检查点放在 AI Studio：

- 数据包：https://aistudio.baidu.com/dataset/detail/384020/intro
- 初始检查点：https://aistudio.baidu.com/dataset/detail/384021/intro

说明：384020 是数据包，不随 GitHub 自动更新；384021 是初始检查点，不是最终 LoRA 权重。最新代码、文档和评估结果以本仓库为准。

## 数据

| 数据源 | 用途 | 数量 |
|---|---|---:|
| Mendeley bilingual prescription | 整页处方 OCR | 997 条可用标注 |
| Bangladesh 200 prescription YOLO | 药品区域检测 | 200 张处方图 |
| RxHandBD | 手写药品词识别 | 4463 训练 / 1115 评估 |

Mendeley 原包有 1000 张图，但 CSV 清洗后只有 997 条唯一可用标注。固定划分后共有 train 4801、val 607、eval 1367。

另外补了 20 张手机实拍图，其中 18 张对应固定 eval，可用于 `realshot_eval_18`；另外 2 张只作为采集示例。

## 基线

RxHandBD 词图：

| 模型 | 图像数 | Exact Match | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0.2197 | 0.4736 |

`realshot_eval_18`：

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.5 | 18 | 11 | 7 | 0.9542 | 0.9124 |
| PaddleOCR-VL v1 本地模型 | 18 | 18 | 0 | 0.9297 | 0.8792 |

这里是零样本结果，不是微调结果。

## LoRA/SFT

训练只用了公开 RxHandBD 词图，没有使用真实线下处方。

| 项目 | 数值 |
|---|---:|
| 基础检查点 | rank8 step512 |
| 轻增强检查点 | aug-light rank8 step512 |
| 基础训练样本 | 3979 |
| 轻增强训练样本 | 3979 原图 + 1800 增强图 |
| 评估样本 | 1115 |
| 推理设置 | `max_new_tokens=32` |

RxHandBD 1115 张词图：

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2386 | 0.4327 | 0.4255 |
| LoRA step512 | 0.2682 | 0.3831 | 0.3783 |
| LoRA aug-light step512 | 0.2825 | 0.3754 | 0.3702 |

`realshot_eval_18`：

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL v1 本地模型 | 18 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA step512 | 18 | 18 | 0 | 0.8729 | 0.8679 |

简单看，`aug-light step512` 在公开词图上最好。它是在 600 张训练图上加了模糊、亮度和旋转扰动后训练出来的。

实拍子集上仍然保留 `LoRA step512` 作为当前结果。`aug-light` 的 max64 版本 18 张都跑完了，但 Micro CER 是 0.9421；max128 版本有 2 张超时，所以不作为实拍结果。

rank4、rank16、重增强和轻增强的对比记录见 `docs/lora_strategy_experiments.md`。

## Demo

Demo 默认使用内置脱敏样例，别人 clone 后可以直接运行，查看图片预览、OCR 文本、JSON 输出和当前指标。页面里的本地 OCR 推理是可选项，需要自己准备 PaddleOCR-VL 环境和模型目录。

```powershell
pip install -r requirements-demo.txt
streamlit run demo\app.py
```

## 复查和测试

```powershell
python -m unittest discover -s tests
python scripts\analyze_word_eval.py --predictions <predictions.jsonl> --output-json outputs\error_analysis.json
```

实拍评估用 warm-worker 脚本跑：模型常驻，单张图片单独计时，卡住后重启 worker 再试，避免一张图拖住整轮评估。

## 主要文件

- `docs/technical_report.md`：数据、质检和指标。
- `docs/data_statistics_report.md`：数据来源、任务类型、难度分布和错误分析入口。
- `docs/realshot_manual_qc.md`：20 张实拍图人工质检。
- `docs/realshot_baseline.md`：`realshot_eval_18` 结果。
- `docs/lora_strategy_experiments.md`：LoRA rank 和增强对比。
- `docs/windows_quick_start.md`：Demo、测试和复查步骤。
- `demo/app.py`：本地 Demo。
- `outputs/lora_eval1115_realshot_summary.json`：当前关键指标摘要。
- `outputs/lora_strategy_experiment_summary.json`：rank 和增强实验摘要。

## 还没做

- 真实线下处方数据暂未补充。
- 实拍子集只有 18 张，每张只有 1 个实拍版本。
- 结构化字段人工标注还不完整。
- 难样本重点训练还没完整跑。
- 药品词典后处理还没系统做。
