# MXF文件分析器

一个基于Python和tkinter开发的GUI工具，用于查看和分析MXF (Material Exchange Format) 文件的内容和结构。

## 功能特性

### 核心功能
- **文件结构查看**: 以树形结构展示MXF文件的分区信息
- **基本信息**: 显示文件大小、分区数量等基本信息
- **十六进制查看器**: 查看文件任意位置的十六进制内容
- **元数据查看**: 显示MXF文件的元数据信息
- **报告导出**: 将分析结果导出为文本报告

### 详细分区信息
- **MXF版本**: 主版本号和次版本号
- **KAG大小**: Key-length-value Alignment Grid大小
- **分区偏移**: 本分区、前一分区、Footer分区的偏移量
- **字节计数**: Header字节数、Index字节数
- **流标识**: Index SID、Body SID
- **Body偏移**: 本质数据的起始位置
- **操作模式**: 自动识别OP1a/1b/1c、OP2a/2b/2c、OP3a/3b/3c等
- **Essence容器**: 识别DV、MPEG、JPEG 2000、DNxHD、AES3/BWF等容器类型

## 系统要求

- Python 3.7 或更高版本
- tkinter (Python标准库)

## 安装

1. 克隆或下载项目到本地
2. 确保已安装Python 3.7+
3. 检查tkinter是否可用（通常已包含在Python安装中）

```bash
# 测试tkinter是否可用
python -m tkinter
```

如果tkinter未安装：
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS**: 通常已包含
- **Windows**: 通常已包含

## 使用方法

### 方式1：直接运行Python程序

```bash
python3 mxf_analyzer.py
```

### 方式2：使用编译后的可执行文件（推荐）

#### 编译成可执行文件

项目提供了两个编译脚本：

**生成单文件可执行版本：**
```bash
./build.sh
```
编译完成后运行：
```bash
./dist/MXF-Analyzer
```

**生成.app应用包版本（推荐）：**
```bash
./build_app.sh
```
编译完成后：
- 双击 `dist/MXF-Analyzer.app` 运行
- 或安装到应用程序文件夹：`cp -r dist/MXF-Analyzer.app /Applications/`

### 使用界面

1. 点击"打开MXF文件"按钮选择要分析的MXF文件

2. 在左侧树形视图中浏览文件结构

3. 在右侧标签页中查看详细信息：
   - **基本信息**: 文件概览和统计信息
   - **分区详情**: 各分区的详细信息（包括版本、KAG大小、操作模式、Essence容器等）
   - **十六进制查看**: 查看文件任意位置的原始字节数据
   - **元数据**: MXF元数据信息

4. 点击树形视图中的分区节点，自动跳转到对应位置的十六进制视图

5. 点击"导出报告"可将分析结果保存为文本文件

## 项目结构

```
mxf-analyzer/
├── mxf_analyzer.py    # GUI主程序
├── mxf_parser.py      # MXF文件解析模块
├── build.sh           # 编译脚本（单文件版本）
├── build_app.sh       # 编译脚本（.app版本）
├── requirements.txt   # 项目依赖
└── README.md         # 项目说明
```

## MXF文件格式说明

MXF (Material Exchange Format) 是一种专业的音视频文件格式，主要用于广播和后期制作领域。

主要特点：
- 基于SMPTE标准
- 使用KLV (Key-Length-Value) 编码
- 包含Header、Body、Footer等分区
- 支持丰富的元数据

## 开发说明

### MXFParser类

核心解析类，负责：
- 识别MXF文件格式（基于SMPTE 377M标准）
- 解析分区结构（Header、Body、Footer）
- 解析分区包详细信息（版本、KAG、偏移量、SID等）
- 识别操作模式（Operational Pattern）
- 识别Essence容器类型
- 提取元数据
- 提供十六进制查看功能

### MXFAnalyzerGUI类

GUI界面类，提供：
- 文件打开和加载
- 树形结构展示
- 多标签页视图（基本信息、分区详情、十六进制、元数据）
- 可调整大小的分割面板
- 用户交互和事件处理
- 报告导出功能

### 编译脚本

- **build.sh**: 使用PyInstaller打包成单文件可执行版本
- **build_app.sh**: 使用PyInstaller打包成.app应用包版本

## 注意事项

1. 本工具主要用于查看和分析MXF文件结构，不支持编辑功能
2. 对于超大文件（>100MB），解析可能需要一些时间，工具会限制搜索范围以提高性能
3. 编译后的可执行文件首次运行时，Mac可能会提示"无法验证开发者"，需要在"系统偏好设置 > 安全性与隐私"中允许运行
4. 编译需要安装PyInstaller，脚本会自动安装
5. 当前版本基于SMPTE 377M标准实现了完整的分区包解析功能

## 后续改进方向

- [x] 支持详细的分区包解析（版本、KAG、偏移量等）
- [x] 识别操作模式（OP1a/1b/1c等）
- [x] 识别Essence容器类型
- [x] 提供编译脚本生成可执行文件
- [ ] 支持更详细的元数据集（Metadata Sets）解析
- [ ] 添加视频/音频流详细信息展示
- [ ] 支持MXF文件完整性验证
- [ ] 添加内容搜索功能
- [ ] 支持更多MXF变体格式（如AS-02、AS-11等）
- [ ] 添加应用程序图标
- [ ] 支持拖拽打开文件

## 许可证

MIT License
