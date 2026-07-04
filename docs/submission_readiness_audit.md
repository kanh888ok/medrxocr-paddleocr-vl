# 提交状态检查

更新时间：2026-05-25

## 当前状态

仓库可以展示数据整理、基线评测和复现实验流程，但仍需要补充自采数据、人工质检结果和微调后指标。

## 公开材料

- GitHub: `https://github.com/kanh888ok/medrxocr-paddleocr-vl`
- AI Studio 数据包: `https://aistudio.baidu.com/dataset/detail/384020/intro`
- 初始检查点: `https://aistudio.baidu.com/dataset/detail/384021/intro`

## 已完成

- 公开数据来源登记。
- 统一 JSONL 格式。
- 固定训练集、验证集、评估集划分。
- 数据统计和质量检查脚本。
- PaddleOCR-VL 风格 SFT 清单。
- ERNIEKit PaddleOCR-VL SFT 清单生成脚本。
- LoRA/SFT 配置文件。
- RxHandBD 词图评估集 zero-shot 基线。
- 初始检查点发布。

## 基线结果

| 模型 | 图像数 | 错误数 | Exact Match | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0 | 0.2197 | 0.4736 |

这些是 zero-shot 词图识别结果，不是 LoRA/SFT 微调结果。

## 还缺什么

- 自行收集的数据。
- 人工标注和质检记录。
- 正式 LoRA/SFT 训练日志。
- 微调后指标。
- 按难度和来源划分的错误分析。
