# ErrorFile

**ErrorFile** 是一个用于检测多种格式文件是否损坏或无效的 Python 库。它旨在帮助开发者在处理文件流时，快速识别并拦截异常数据。

## 安装指南

您可以根据实际需求选择安装核心包或特定的功能扩展。

安装最小核心包（仅包含基础功能）：

```bash
pip install ErrorFile

```

按需安装特定格式的插件依赖：

```bash
pip install ErrorFile[pdf]      # PDF 支持
pip install ErrorFile[image]    # 图像支持
pip install ErrorFile[office]   # Office 文档支持
pip install ErrorFile[archive]  # 压缩包支持
pip install ErrorFile[media]    # 音视频媒体支持

```

一键安装所有可选依赖：

```bash
pip install ErrorFile[all]

```

您也可以组合安装多个扩展：

```bash
pip install ErrorFile[pdf,image,office]

```

## 快速上手

以下示例展示了如何对指定文件进行深度完整性检查。

```python
from ErrorFile import inspect_file

# 定义待检测文件的绝对或相对路径
file_path = r"tests/files/TOM_损坏.jpg"

# 执行文件检测
# param mode: "deep" 模式会解析文件结构，比仅检查文件头的 "fast" 模式更准确，但会有更多的计算和 IO 开销
# return: (is_ok, message) 元组，分别代表文件是否健康及相关描述信息
is_ok, message = inspect_file(file_path, mode="deep")

# 输出检测结果日志
print(f"File: {file_path}\nOK: {is_ok}\nMessage: {message}")

```

## 检测模式

为了在性能与准确性之间取得平衡，库提供了以下几种检测模式：

* **`fast`**：仅进行快速的结构性检查（如文件头/魔数校验），适用于高吞吐量场景。
* **`deep`**：进行更深层次的文件解析，能覆盖更多的损坏场景（推荐用于对准确性要求较高的场景）。
* **`precise`**：`deep` 模式的别名，用于保持向后兼容性。

## 公共 API

### `inspect_file(file_path, mode="deep", ...)`

这是最常用的基础接口。

* **返回值**：默认返回 `(ok, message)` 元组。

### `inspect_file_report(file_path, mode="deep", ...)`

提供更详尽的检测数据。

* **返回值**：返回一个 `InspectionReport` 对象，其中包含标签（tags）、耗时统计、缓存命中元数据以及标准化后的模式名称。

### `inspect_files(file_paths, mode="deep", staged_deep=False, ...)`

用于批量处理的 API。

* **特性**：内置路径去重功能。
* **staged_deep**：可选参数，支持分阶段深度检测策略。

## 插件架构

ErrorFile 采用内部插件机制，根据文件扩展名动态注册对应的检查器（Inspector）。

**默认内置插件：**

* 图像插件 (Image Plugin)
* PDF 插件 (PDF Plugin)
* Office 文档插件 (Office Plugin)
* 归档文件插件 (Archive Plugin)
* 多媒体插件 (Media Plugin)
* 文本插件 (Text Plugin)

**容错加载机制：**
如果环境中缺少某个插件所需的依赖库（例如未安装 `pypdf`），系统会在加载时自动跳过该插件，而不会导致整个包导入失败（Crash）。

您可以查看当前的插件加载状态：

```python
from ErrorFile.Detection.FileInspector import DEFAULT_LOADED_PLUGINS, DEFAULT_SKIPPED_PLUGINS

# 打印已成功加载的插件列表
print(DEFAULT_LOADED_PLUGINS)
# 打印因依赖缺失而被跳过的插件列表
print(DEFAULT_SKIPPED_PLUGINS)

```

### 自定义扩展

您可以注册自定义的检查逻辑：

**方式一：注册单个检查器**

```python
from ErrorFile.Detection.FileInspector import register_inspector
from ErrorFile.report import ok_finding

def check_dummy(path: str, mode: str):
    """
    针对 .dummy 文件的自定义检查逻辑
    注意：此函数将被框架回调，需确保内部异常处理机制完善
    """
    # 返回标准化的成功结果对象
    return ok_finding("Dummy check passed")

# 注册针对 .dummy 后缀的检查函数
register_inspector(".dummy", check_dummy)

```

**方式二：注册插件注册器**

```python
from ErrorFile.Detection.FileInspector import register_plugin

def register(registry):
    """
    批量注册检查器的回调函数
    :param registry: 全局检查器注册表 (Dict)
    """
    # 使用 lambda 或具体函数注册对应后缀的处理逻辑
    registry[".abc"] = lambda path, mode: ...

# 将注册函数加入插件加载流程
register_plugin(register)

```

## 支持的文件类型

目前的检测覆盖范围包括：

* **图像**：`jpeg/jpg/png/gif/bmp/webp/tiff/svg`
* **PDF**：`pdf`
* **Office 文档**：`xlsx/xls/docx/pptx`
* **归档/压缩包**：`zip/rar/7z/tar/tar.gz/tar.bz2/tar.xz/gz/bz2/xz`
* **多媒体**：`mp3/mp4/flac/ogg/oga/wav`
* **文本及结构化数据**：`txt/md/log/csv/tsv/html/htm/ini/cfg/json/ndjson/xml/toml/yaml/yml/rtf/eml/msg/sqlite/db`

## 注意事项

* **签名预检**：针对特定的文件格式，系统默认启用了文件签名（Magic Number）预检功能，以快速过滤明显错误的文件。
* **并行处理与缓存**：当在批量 API 中启用基于进程的并行模式（Process-based parallel mode）时，内存缓存功能将自动禁用，以避免进程间数据不一致或内存开销过大。

## 许可证

Apache-2.0。详情请参阅项目中的 `LICENSE` 文件。