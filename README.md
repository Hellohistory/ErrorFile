# ErrorFile

`ErrorFile`是一个用于检测和识别各种文件错误的Python包，包括图片、PDF、Excel和Word文件。通过使用不同的检测模式，可以快速或精确地识别文件中的潜在问题。

## 安装

你可以通过pip安装`ErrorFile`：

```bash
pip install ErrorFile
```

## 快速开始

使用`ErrorFile`非常简单。首先，导入`FileInspector`类，然后创建一个实例，并指定要检查的文件路径和（可选的）检查模式。

### 示例

```python
from Detection.FileInspector import FileInspector

file_path = r'tests/files/TOM_损坏.jpg'
image_mode = 'precise'  # 或 'fast'
result = FileInspector(file_path, image_mode).inspect()
print(result)
```

## 支持的文件类型

目前，`ErrorFile`支持以下文件类型的检查：

- 图片（JPEG, JPG, PNG, GIF, BMP, WEBP, TIFF, SVG）
- PDF
- Excel（XLSX, XLS）
- Word（DOCX）

## 检测模式

对于图片文件，支持两种检测模式：

- `fast`：快速检测模式，适用于快速概览和检查大量文件。
- `precise`：精确检测模式，适用于深入分析单个文件。

对于PDF、Excel和Word文件，将自动采用详细检测模式。

## API参考

### `FileInspector`

主要的类，用于初始化文件检查过程。

#### 参数

- `file_path`：要检查的文件路径。
- `image_mode`：（可选）图片检查模式，默认为`precise`。

#### 方法

- `inspect()`：执行文件检查，并返回检查结果。

## 贡献

欢迎贡献！如果你有任何建议或改进，请提交Pull Request或创建Issue。

## 许可证

`ErrorFile`根据Apache-2.0许可证发布。有关详细信息，请查看LICENSE文件。
