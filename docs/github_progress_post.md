# GitHub Progress Post Template

【报名】：1
【选题方向】：医疗处方识别
【团队人数】：1

项目进展：

我正在构建 MedRxOCR，一个基于 PaddleOCR-VL 的多语种医疗处方结构化识别衍生模型。项目目标不是普通 OCR，而是将真实处方图像解析为结构化 JSON，包括药品名、剂量、用法、频次、疗程、科室、日期、医生签名/印章等字段。

当前设计包括：

1. 使用公开许可、已脱敏的真实处方数据构建评估集。
2. 统一转换为 MedRxOCR JSON schema。
3. 支持 full-page OCR、药品区域检测、手写药品词识别、药品行结构化解析等子任务。
4. 基于 PaddleOCR-VL / PaddleOCR-VL-1.5 进行 LoRA SFT。
5. 引入药品词典约束，用于 drug_name normalization、剂量单位标准化、频次/给药途径规范化。
6. 开源数据转换、质控、评估脚本和本地 Demo。

项目重点关注真实医疗处方中的手写、印章遮挡、拍照倾斜、低清晰度、多语言混排和药品缩写等长尾难点。
