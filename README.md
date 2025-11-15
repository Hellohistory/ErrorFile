# ErrorFile

`ErrorFile`是一个用于检测和识别各种文件错误的Python包，包括图片、PDF、Excel和Word文件。通过使用统一的顶层接口，可以快速定位文件中潜在的问题。

## 安装

你可以通过pip安装`ErrorFile`：

```bash
pip install ErrorFile
```

## 快速开始

使用`ErrorFile`非常简单。推荐直接使用顶层函数`inspect_file`：

```python
from ErrorFile import inspect_file

file_path = r'tests/files/TOM_损坏.jpg'
# mode 参数由 inspect_file 统一处理，当前仅支持 'precise'
is_ok, message = inspect_file(file_path, mode='precise')
print(f"File: {file_path}\nOK: {is_ok}\nMessage: {message}")
```

## 支持的文件类型

目前，`ErrorFile`支持以下文件类型的检查：

- 图片（JPEG, JPG, PNG, GIF, BMP, WEBP, TIFF, SVG）
- PDF
- Office 文档（Excel：XLSX、XLS；Word：DOCX；PowerPoint：PPTX）
- 压缩包（ZIP、RAR）
- 媒体文件（MP3、MP4）

## 检测模式

图片文件采用精确检测模式(`precise`)，底层基于 Pillow 的 `verify()` 与 `load()` 方法，能够快速且可靠地发现问题。非图片文件会自动执行相应的深度检查，无需手动配置模式。

## API参考

### `inspect_file(file_path, mode='precise')`

顶层函数，用于检查指定路径的文件是否损坏。

#### 参数

- `file_path`：要检查的文件路径。
- `mode`：（可选）图片检测模式，目前仅支持 `precise`，其它文件类型忽略此参数。

#### 返回

- `(is_ok, message)`：`is_ok`是布尔值，表示文件是否通过检查；`message`是详细描述信息。

## 贡献

欢迎贡献！如果你有任何建议或改进，请提交Pull Request或创建Issue。

## 许可证

`ErrorFile`根据Apache-2.0许可证发布。有关详细信息，请查看LICENSE文件。
