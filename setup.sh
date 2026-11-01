#!/bin/bash
# ============================================
# Lyrics MV Pipeline 一键安装
# 用法: bash setup.sh
# ============================================

set -e
cd "$(dirname "$0")"

echo "🎵 Lyrics MV Pipeline 安装"
echo "=========================="

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.8+"
    exit 1
fi
echo "✅ Python $(python3 --version | cut -d' ' -f2)"

# 2. 检查 FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  未找到 FFmpeg，请安装:"
    echo "   Ubuntu: sudo apt install ffmpeg"
    echo "   macOS:  brew install ffmpeg"
else
    echo "✅ FFmpeg $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"
fi

# 3. 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 4. 安装依赖
source venv/bin/activate
pip install --upgrade pip -q
pip install Pillow pysubs2 requests psutil -q
echo "✅ 依赖安装完成"

# 5. 下载中文字体
mkdir -p fonts
if ! ls fonts/*.ttf fonts/*.TTF 2>/dev/null | head -1 > /dev/null; then
    echo "⬇️  下载中文字体..."
    curl -L -o fonts/NotoSansSC.ttf \
        "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf" \
        --connect-timeout 15 -s 2>/dev/null
    echo "✅ 字体下载完成"
fi

# 6. 创建目录
mkdir -p archive web_output logs
echo "✅ 目录创建完成"

# 7. 配置文件
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ 配置模板已创建 (.env)"
    echo "⚠️  请编辑 .env 填入你的凭证!"
fi

echo ""
echo "=========================="
echo "🎉 安装完成！"
echo ""
echo "下一步:"
echo "  1. 编辑 .env 填入凭证"
echo "  2. python scripts/select_song.py --test"
echo "  3. 查看 AI_GUIDE.md 了解完整流程"
echo "=========================="
