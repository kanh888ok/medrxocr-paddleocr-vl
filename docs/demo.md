# Demo 说明

本项目提供一个轻量 Streamlit Demo，用于展示处方 OCR 项目的输入、结构化输出格式和当前评估结果。

运行方式：

```powershell
pip install -r requirements.txt
streamlit run demo\app.py
```

Demo 页面包含三部分：

- 上传处方图片。
- 粘贴 OCR 文本并生成统一 JSON 结构。
- 查看 PaddleOCR-VL baseline 与 LoRA step512 的评估对比。

当前 Demo 不内置模型权重，也不把原始图片上传到 GitHub。真实推理需要先按 README 准备 PaddleOCR-VL 环境和本地模型文件。
