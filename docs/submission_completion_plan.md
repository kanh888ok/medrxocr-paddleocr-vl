# 后续补充计划

## 已有材料

- GitHub: `https://github.com/kanh888ok/medrxocr-paddleocr-vl`
- AI Studio 数据包: `https://aistudio.baidu.com/dataset/detail/384020/intro`
- 初始检查点: `https://aistudio.baidu.com/dataset/detail/384021/intro`
- 技术报告: `docs/technical_report.md`

## 已完成

- 公开数据下载和校验。
- 数据转换为统一 JSONL。
- 固定训练集、验证集、评估集。
- 生成 SFT 训练清单。
- 生成质量检查和数据统计。
- 完成 RxHandBD 词图评估集 zero-shot 基线。
- 发布初始检查点。

## 当前基线

| 模型 | 图像数 | 错误数 | Exact Match | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0 | 0.2197 | 0.4736 |

这些指标只说明未微调模型在词图评估集上的表现。

## 下一步

- 补充自采处方数据。
- 写清楚标注规则和质检结果。
- 跑正式 LoRA/SFT 训练。
- 在固定评估集上报告微调后指标。
- 增加错误分析。
