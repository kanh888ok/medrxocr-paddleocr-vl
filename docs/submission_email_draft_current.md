# 提交邮件草稿

主题：

PaddleOCR 衍生模型挑战赛 - MedRxOCR 处方 OCR - kanh888ok

收件人：

ext_paddle_oss@baidu.com
paddleocr@baidu.com
cuicheng01@baidu.com
liujiaxuan01@baidu.com

正文：

各位老师好：

我提交的项目是 MedRxOCR，方向是医疗处方 OCR。

项目基于公开且已脱敏的处方数据，整理了统一 JSONL 格式、固定训练/验证/评估划分、质量检查脚本、数据统计脚本、PaddleOCR-VL 评测脚本和 SFT 训练清单。

当前已完成的基线结果如下：

| 模型 | 数据集 | 图像数 | 错误数 | Exact Match | Micro CER |
|---|---|---:|---:|---:|---:|
| PaddleOCR-VL | RxHandBD 词图评估集 | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | RxHandBD 词图评估集 | 1115 | 0 | 0.2197 | 0.4736 |

这些结果是 zero-shot 词图识别基线，不是微调后指标。

项目也发布了一个初始检查点，供后续训练和复现实验使用。正式微调结果还需要在固定评估集上继续补充。

材料链接：

1. GitHub 仓库
https://github.com/kanh888ok/medrxocr-paddleocr-vl

2. AI Studio 数据包
https://aistudio.baidu.com/dataset/detail/384020/intro

3. AI Studio 初始检查点
https://aistudio.baidu.com/dataset/detail/384021/intro

4. 技术报告
https://github.com/kanh888ok/medrxocr-paddleocr-vl/blob/main/docs/technical_report.md

谢谢。

kanh888ok
