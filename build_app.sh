#!/bin/bash

# MXF Analyzer 编译脚本 - 生成.app应用包
# 用于将Python程序打包成Mac .app应用程序

set -e  # 遇到错误立即退出

echo "=========================================="
echo "MXF Analyzer 编译脚本 (.app版本)"
echo "=========================================="
echo ""

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3.7+"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"
echo ""

# 检查pip3是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip"
    exit 1
fi

echo "✓ pip版本: $(pip3 --version)"
echo ""

# 安装PyInstaller
echo "正在检查PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller未安装，正在安装..."
    pip3 install pyinstaller
    echo "✓ PyInstaller安装完成"
else
    echo "✓ PyInstaller已安装"
fi
echo ""

# 清理之前的构建
echo "清理之前的构建文件..."
rm -rf build dist *.spec
echo "✓ 清理完成"
echo ""

# 使用PyInstaller打包成.app
echo "开始打包应用程序(.app格式)..."
echo "这可能需要几分钟时间，请耐心等待..."
echo ""

python3 -m PyInstaller \
    --name="MXF-Analyzer" \
    --windowed \
    --onedir \
    --add-data="mxf_parser.py:." \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    --hidden-import=tkinter.filedialog \
    --hidden-import=tkinter.messagebox \
    --hidden-import=tkinter.scrolledtext \
    --osx-bundle-identifier=com.alibaba.mxf-analyzer \
    --clean \
    mxf_analyzer.py

echo ""
echo "=========================================="
echo "✓ 编译完成！"
echo "=========================================="
echo ""
echo "应用程序位置: dist/MXF-Analyzer.app"
echo ""
echo "使用方法："
echo "  方式1: 双击 dist/MXF-Analyzer.app 运行"
echo "  方式2: 在终端运行: open dist/MXF-Analyzer.app"
echo ""
echo "如需安装到应用程序文件夹："
echo "  cp -r dist/MXF-Analyzer.app /Applications/"
echo ""
echo "注意: 首次运行可能需要在系统偏好设置中允许运行"
echo ""
