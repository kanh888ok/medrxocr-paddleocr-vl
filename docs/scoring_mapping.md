# Scoring Mapping: How MedRxOCR Targets 100 Points

## 1. 评估集质量：20 分

### 我们的设计

- 主评估集使用公开许可的真实脱敏处方数据。
- 统一转换为 MedRxOCR JSON schema。
- 每张图记录 source_id、license、visual_tags、difficulty、pii_redacted。
- 生成 dataset statistics 和 quality audit 报告。
- 建立 easy / medium / hard 难度分层。

### 对应文件

- `docs/data_source_registry.csv`
- `docs/dataset_card.md`
- `scripts/quality_audit.py`
- `scripts/dataset_stats.py`
- `data/eval/*.jsonl`

## 2. 场景稀缺性：15 分

### 我们的设计

- 场景：医疗处方识别。
- 特征：医生手写、药品名、剂量单位、频次缩写、用法、印章/签名遮挡、多语言混排。
- 行业价值：药房自动录入、医疗理赔、处方归档、药品安全审核前置。

## 3. 任务复杂度：15 分

### 我们的任务不是普通 OCR

子任务：

1. full-page OCR
2. prescription field extraction
3. medication-line parsing
4. drug-name normalization
5. medicine-region detection
6. handwritten prescription word recognition
7. JSON validity and clinical-field consistency check

## 4. 训练数据集构建科学性：20 分

### 我们的设计

- source registry
- license/provenance table
- annotation guideline
- automatic quality audit
- duplicate/leakage check
- dataset statistics report

## 5. 微调策略与创新：10 分

### 基础

- PaddleOCR-VL zero-shot
- PaddleOCR-VL-1.5 zero-shot
- LoRA SFT
- multi-task SFT

### 创新点

**Lexicon-Constrained Prescription Decoding**

OCR/VLM 输出后使用药品词典、剂量单位规则、频次缩写表做结构化纠错：

- drug_name_raw -> drug_name_normalized
- mg/ml/tablet/capsule 单位标准化
- bid/tid/qd/qid/prn 频次标准化
- po/iv/im/inh/topical 给药途径标准化

## 6. 技术文档与开源贡献：20 分

### 必备材料

- README
- Dataset Card
- Model Card
- Annotation Guideline
- Privacy & License Note
- Evaluation Script
- Quality Audit Script
- Demo
- Training Config
- Baseline Result Table
