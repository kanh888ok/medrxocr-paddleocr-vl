# 数据获取计划

## 基本原则

1. 不伪造真实临床处方。
2. 合成数据只能作为训练增强，不能放进核心评估集。
3. 每个公开数据源都记录 URL、许可证、用途和风险。
4. 评估集优先使用真实采集、已脱敏、许可证明确的数据。
5. 公开数据不能只改名提交，必须说明清洗、转换和评测口径。

## 优先数据源

### 1. Mendeley bilingual prescription

- URL: https://data.mendeley.com/datasets/tg2hm7n2bs/2
- 内容：1000 张医疗处方图片，含 Bangla / English 文本标注。
- 许可证：CC BY 4.0。
- 用途：整页处方 OCR，训练/验证/评估划分。
- 注意：CSV 清洗后只有 997 条唯一可用标注。

### 2. Bangladesh 200 prescription YOLO

- URL: https://data.mendeley.com/datasets/k62rfd23kz/2
- 内容：200 张已脱敏处方图，含药品名称区域 YOLO 框。
- 许可证：CC BY 4.0。
- 用途：药品区域检测。
- 注意：只有区域框，不等于完整结构化处方标注。

### 3. RxHandBD

- URL: https://data.mendeley.com/datasets/dsb5r6vskg/3
- 内容：5578 张手写处方词图。
- 许可证：CC BY 4.0。
- 用途：手写药品词识别。
- 注意：这是词图数据，不是整页处方数据。

## 可选辅助数据

### CHIP2022 医疗清单发票 OCR

- URL: https://tianchi.aliyun.com/dataset/131815
- 用途：中文医疗票据和表格 KIE 辅助训练。
- 注意：不是处方，不作为主评估集。

### 中文医疗化验单数据集

- URL: https://tianchi.aliyun.com/dataset/126039
- 用途：中文医疗表格结构识别辅助训练。
- 注意：不是处方，不作为主评估集。

### CASIA-HWDB

- URL: https://nlpr.ia.ac.cn/databases/handwriting/home.html
- 用途：中文手写识别辅助训练。
- 注意：不是医疗数据，不作为主评估集。

## 词典资源

### RxNorm

- URL: https://www.nlm.nih.gov/research/umls/rxnorm/index.html
- 用途：英文药品名规范化。

### openFDA Drug Labeling

- URL: https://open.fda.gov/apis/drug/label/
- 用途：英文药品说明和药品词表扩充。

### NMPA 国家药监局数据查询

- URL: https://www.nmpa.gov.cn/datasearch/home-index.html
- 用途：中文药品名称、剂型、规格词表参考。
- 注意：避免未经许可的大规模抓取。

## 当前组合

| 模块 | 来源 | 用途 |
|---|---|---|
| 整页 OCR | Mendeley bilingual | 训练和评估 |
| 区域检测 | Bangladesh 200 | 药品区域框 |
| 词图识别 | RxHandBD | 手写词识别 |
| 词典 | RxNorm / openFDA / NMPA | 后续规范化 |

## 不能做

- 不能把合成数据说成真实处方。
- 不能抓取未授权医院处方截图。
- 不能公开未脱敏处方。
- 不能让核心评估集主要由合成图组成。
- 不能只下载公开数据后改名提交。
