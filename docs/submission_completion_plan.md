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
- 完成 20 张实拍图片人工质检，其中 18 张可计入严格 eval。
- 完成 PaddleOCR-VL-1.5 在 18 张实拍 eval 子集上的零样本基线。
- 完成实拍预处理小试，简单缩放和灰度增强没有带来收益。
- 完成 LoRA/SFT 启动条件检查，当前缺少训练依赖和本地 `data/processed` 清单。
- 发布初始检查点。

## 当前基线

| 模型 | 图像数 | 错误数 | Exact Match | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0 | 0.2197 | 0.4736 |

这些指标只说明未微调模型在词图评估集上的表现。

## 下一步

- 补充真实线下处方数据。
- 补充结构化字段人工标注和字段级质检结果。
- 恢复 AI Studio 数据包中的 `data/processed` 并安装训练依赖。
- 先跑 20-100 条样本的 LoRA/SFT smoke training。
- 在固定评估集上报告微调后指标。
- 增加错误分析。
