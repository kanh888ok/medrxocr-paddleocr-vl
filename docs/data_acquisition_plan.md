# Data Acquisition Plan

## 核心原则

1. 不伪造真实临床处方。
2. 合成数据只用于训练增强，不作为主评估集。
3. 每个公开数据源都要记录 URL、许可证、用途、风险。
4. 主评估集必须优先使用真实采集、已脱敏、许可证明确的数据。
5. 公共数据不能简单搬运，必须重新统一 schema、质控、分层评估和任务定义。

## P0 数据源：必须优先下载

### 1. Image-to-Text Bilingual Dataset from Medical Prescriptions

- URL: https://data.mendeley.com/datasets/tg2hm7n2bs/2
- 类型：1000 张医疗处方手写图像 + Bangla/English 标注。
- 许可证：CC BY 4.0。
- 推荐用途：主评估集核心 + 训练切分。
- 项目中的处理方式：
  - 保留原始 full_ocr_text。
  - 转为 MedRxOCR schema。
  - 添加 language、difficulty、visual_tags。
  - 抽取药品相关行作为 medication-line 子任务。
- 风险：
  - 公开数据不能只是搬运；必须做新的评估协议与结构化标注。

### 2. A Curated Bangladesh-Based Dataset of Handwritten and Printed Prescription Images

- URL: https://data.mendeley.com/datasets/k62rfd23kz/2
- 类型：200 张脱敏处方图，含印刷/手写/mixed；药品名称区域 YOLO 框。
- 许可证：CC BY 4.0。
- 推荐用途：
  - 药品区域检测。
  - full-page hard-case subset。
- 项目中的处理方式：
  - 转 YOLO 标注为 region-level JSON。
  - 做 medicine region detection metric。
  - 可补充人工 full text / medication line 标注。

### 3. RxHandBD

- URL: https://data.mendeley.com/datasets/dsb5r6vskg/3
- 类型：5578 个从实体处方中裁剪的手写词图。
- 许可证：CC BY 4.0。
- 推荐用途：
  - 手写药品/剂型/医嘱词级识别。
  - 作为 word-level subtask。
- 项目中的处理方式：
  - 保留官方 80/20 train/test。
  - 将 label 转成 OCR SFT 样本。
  - 报告 word-level accuracy / CER。

## P1 国内辅助数据源

### 4. CHIP2022 医疗清单发票 OCR 要素提取任务

- URL: https://tianchi.aliyun.com/dataset/131815
- 用途：中文医疗票据和医疗表格 KIE 辅助训练。
- 注意：不是处方，不作为主评估集。

### 5. 中文医疗化验单数据集

- URL: https://tianchi.aliyun.com/dataset/126039
- 用途：中文医疗表格结构识别辅助训练。
- 注意：不是处方，不作为主评估集。

### 6. CASIA-HWDB

- URL: https://nlpr.ia.ac.cn/databases/handwriting/home.html
- 用途：中文手写识别辅助训练。
- 注意：不是医疗，不作为主评估集。

### 7. SCUT-HCCDoc

- URL: https://github.com/HCIILAB/SCUT-HCCDoc_Dataset_Release
- 用途：中文相机拍摄手写文档鲁棒性训练。
- 注意：检查申请/许可条件，不公开重分发。

## LEXICON 数据源

### RxNorm

- URL: https://www.nlm.nih.gov/research/umls/rxnorm/index.html
- 用途：英文药品名规范化、商品名/通用名映射。

### openFDA Drug Labeling

- URL: https://open.fda.gov/apis/drug/label/
- 用途：英文药品说明、药品词表扩充。

### NMPA 国家药监局数据查询

- URL: https://www.nmpa.gov.cn/datasearch/home-index.html
- 用途：中文药品名称/剂型/规格词表构建参考。
- 注意：避免未经许可的大规模爬取。

## 推荐数据组合

| 模块 | 来源 | 目标用途 |
|---|---|---|
| full-page OCR/KIE | Mendeley 1000 | 主评估 + SFT |
| detection | Mendeley 200 + Roboflow | 药品区域检测 |
| word recognition | RxHandBD | 手写药品词识别 |
| Chinese medical KIE | 天池医疗票据/化验单 | 辅助训练 |
| Chinese handwriting | CASIA/SCUT | 辅助训练 |
| lexicon | RxNorm/openFDA/NMPA | 字段规范化 |

## 不能做的事

1. 不能把 synthetic 数据说成真实处方。
2. 不能抓无授权医院处方截图。
3. 不能公开未脱敏处方。
4. 不能让评估集主要由合成图组成。
5. 不能只下载公开数据然后改名提交。
