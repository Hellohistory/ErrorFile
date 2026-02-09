# ErrorFile

`ErrorFile`是一个用于检测和识别多种文件损坏/格式异常的Python包。它提供统一的顶层接口，可快速定位文件中潜在问题。

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
# mode 支持 'fast' 或 'deep'；'precise' 兼容映射到 'deep'
is_ok, message = inspect_file(file_path, mode='deep')
print(f"File: {file_path}\nOK: {is_ok}\nMessage: {message}")
```

## 支持的文件类型

目前，`ErrorFile`支持以下文件类型的检查：

- 图片（JPEG, JPG, PNG, GIF, BMP, WEBP, TIFF, SVG）
- PDF
- Office 文档（Excel：XLSX、XLS；Word：DOCX；PowerPoint：PPTX）
- 压缩包（ZIP、RAR、7z、TAR、TAR.GZ、TAR.BZ2、TAR.XZ、GZ、BZ2、XZ）
- 媒体文件（MP3、MP4、FLAC、OGG、OGA、WAV）
- 文本文件（TXT、MD、LOG、CSV、TSV、HTML/HTM、INI/CFG、JSON、NDJSON、XML、TOML、YAML/YML、RTF、EML）
- 其他结构化文件（MSG、SQLite：SQLITE/DB）

## 检测模式

`mode` 支持：
- `fast`：快速结构检查，适合批量初筛。
- `deep`：深度内容检查，覆盖更多损坏场景。

兼容性说明：传入 `precise` 会被自动映射为 `deep`。

性能说明：框架会先进行轻量文件头签名预检，并在批量检测时自动合并重复路径，减少不必要的深度解析开销。

## API参考

### `inspect_file(file_path, mode='deep')`

顶层函数，用于检查指定路径的文件是否损坏。

#### 参数

- `file_path`：要检查的文件路径。
- `mode`：（可选）检测模式，支持 `fast` 与 `deep`，默认 `deep`。`precise` 作为兼容别名会映射为 `deep`。
- `signature_precheck`：（可选）是否启用文件头签名预检，默认 `True`。
- `signature_precheck_allowlist` / `signature_precheck_denylist`：（可选）控制哪些扩展名参与签名预检。

#### 返回

- `(is_ok, message)`：`is_ok`是布尔值，表示文件是否通过检查；`message`是详细描述信息。

### `inspect_files(..., staged_deep=False)`

- `staged_deep=True` 且 `mode='deep'` 时，批量检测会先执行 `fast`，仅对通过 `fast` 的文件继续 `deep`，提升混合坏样本场景的吞吐。

## 性能基准

可使用脚本对比 `staged_deep` 的收益：

```bash
python scripts/benchmark_staged_deep.py --samples 1200 --bad-ratio 0.7 --workers 8 --repeats 3
```

也可关闭签名预检进行对照：

```bash
python scripts/benchmark_staged_deep.py --samples 1200 --bad-ratio 0.7 --workers 8 --repeats 3 --disable-signature-precheck
```

## 贡献

欢迎贡献！如果你有任何建议或改进，请提交Pull Request或创建Issue。

## 许可证

`ErrorFile`根据Apache-2.0许可证发布。有关详细信息，请查看LICENSE文件。
