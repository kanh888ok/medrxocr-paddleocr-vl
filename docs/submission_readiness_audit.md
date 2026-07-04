# 提交状态检查

更新时间：2026-05-25

## 当前状态

仓库可以展示数据整理、基线评测、实拍子集质检和复现实验流程，但仍需要补充真实线下处方数据、结构化人工标注和微调后指标。

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
- 20 张实拍图片人工质检，其中 18 张可计入严格 eval。
- PaddleOCR-VL-1.5 在 18 张实拍 eval 子集上的零样本基线。
- 实拍图像预处理小试，简单缩放和灰度增强没有带来收益。
- LoRA/SFT 启动条件检查。
- 初始检查点发布。

## 基线结果

| 模型 | 图像数 | 错误数 | Exact Match | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL | 1115 | 0 | 0.2386 | 0.4255 |
| PaddleOCR-VL-1.5 | 1115 | 0 | 0.2197 | 0.4736 |

这些是 zero-shot 词图识别结果，不是 LoRA/SFT 微调结果。

## 还缺什么

- 真实线下处方自采数据。
- 结构化字段人工标注记录。
- 正式 LoRA/SFT 训练日志。
- 微调后指标。
- 可运行训练环境和本地 `data/processed` 清单。
- 按难度和来源划分的错误分析。
