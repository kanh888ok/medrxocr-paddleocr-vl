# MedRxOCR 处方 OCR 数据集

这个仓库整理了几份公开处方数据，用来做 PaddleOCR-VL 的处方 OCR 评测和小规模 LoRA/SFT 实验。

代码、配置和小结果放在 GitHub。原始图片、大 JSONL、模型权重和检查点放在 AI Studio：

- 数据包：https://aistudio.baidu.com/dataset/detail/384020/intro
- 初始检查点：https://aistudio.baidu.com/dataset/detail/384021/intro

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
| 检查点 | step512 |
| LoRA rank | 8 |
| 训练样本 | 3979 |
| 评估样本 | 1115 |
| 推理设置 | `max_new_tokens=32` |
| train loss | 2.8878 |

RxHandBD 1115 张词图：

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2386 | 0.4327 | 0.4255 |
| LoRA step512 | 0.2682 | 0.3831 | 0.3783 |

`realshot_eval_18`：

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL v1 本地模型 | 18 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA step512 | 18 | 18 | 0 | 0.8729 | 0.8679 |

简单看，`step512` 比基线好一些。realshot 的提升不大，但至少同一批 18 张图上方向是正的。`step1024` 前 100 张更高，但后面推理不稳定，暂时不作为推荐结果。

## Demo

Demo 只是展示图片输入、OCR 文本和 JSON 输出格式，字段提取还不完整。

```powershell
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
- `docs/realshot_manual_qc.md`：20 张实拍图人工质检。
- `docs/realshot_baseline.md`：`realshot_eval_18` 结果。
- `demo/app.py`：本地 Demo。
- `outputs/lora_eval1115_realshot_summary.json`：当前关键指标摘要。

## 还没做

- 真实线下处方数据暂未补充。
- 实拍子集只有 18 张，每张只有 1 个实拍版本。
- 结构化字段人工标注还不完整。
- 数据增强、LoRA rank 16/32、多阶段训练、药品词典后处理还没系统做。
