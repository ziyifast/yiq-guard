#!/bin/bash
# yiQGuard 一键打包脚本
# 用法：
#   bash build.sh           正式打包
#   bash build.sh --alias   别名模式（快速测试，不可分发）
#   bash build.sh --run     直接运行（不打包）

set -e

echo "═══════════════════════════════════════════"
echo "  yiQGuard 打包工具"
echo "═══════════════════════════════════════════"
echo ""

# ── 检测可用的 Python ─────────────────────────────────────────
# 优先使用 python3，避免 conda base 环境干扰
detect_python() {
    # 如果已在 venv 中，直接用 venv 的 python
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "python3"
        return
    fi

    # 检测是否在 conda 环境中
    if [ -n "$CONDA_DEFAULT_ENV" ] && [ "$CONDA_DEFAULT_ENV" != "base" ]; then
        echo "⚠️  检测到 conda 环境: $CONDA_DEFAULT_ENV" >&2
        echo "   建议退出 conda 后再运行: conda deactivate" >&2
    fi

    # 优先查找系统 python3 或 homebrew python
    for py in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$py" &>/dev/null; then
            local ver=$("$py" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
            local major=$(echo "$ver" | cut -d. -f1)
            local minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
                echo "$py"
                return
            fi
        fi
    done
    echo "python3"
}

PYTHON_CMD=$(detect_python)
PY_VERSION=$($PYTHON_CMD --version 2>&1)
echo "✓ Python: $PY_VERSION ($PYTHON_CMD)"

# ── 检查/创建虚拟环境 ─────────────────────────────────────────
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        echo "✓ 激活已有 venv..."
        source venv/bin/activate
    else
        echo "  创建虚拟环境 (venv)..."
        $PYTHON_CMD -m venv venv
        source venv/bin/activate
        echo "  升级 pip..."
        pip install --upgrade pip -q 2>/dev/null || true
    fi
fi

echo "✓ venv: $VIRTUAL_ENV"
echo "✓ venv Python: $(python --version)"
echo ""

# ── 安装依赖 ──────────────────────────────────────────────────
echo "安装依赖..."
pip install -r requirements.txt -q 2>&1 | grep -v "already satisfied" || true
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 依赖安装失败！尝试："
    echo "   1. xcode-select --install（安装编译工具）"
    echo "   2. pip install --upgrade pip"
    echo "   3. 使用清华镜像: pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
    exit 1
fi

pip install py2app -q 2>&1 | grep -v "already satisfied" || true
echo "✓ 依赖就绪"
echo ""

# ── 执行操作 ──────────────────────────────────────────────────
if [ "$1" == "--run" ]; then
    echo "═══ 直接运行 ═══"
    echo ""
    python main.py
    exit 0
fi

# 清理旧构建
rm -rf build/ dist/ .eggs/
echo "✓ 旧构建已清理"
echo ""

if [ "$1" == "--alias" ] || [ "$1" == "-A" ]; then
    echo "═══ 别名模式（快速测试）═══"
    echo ""
    python setup.py py2app -A 2>&1 | tail -5
    echo ""
    if [ -d "dist/yiQGuard.app" ]; then
        echo "✅ 完成！运行: open dist/yiQGuard.app"
    else
        echo "❌ 打包失败，查看上方错误输出"
        exit 1
    fi
else
    echo "═══ 正式打包 ═══"
    echo ""
    python setup.py py2app 2>&1 | tail -10
    echo ""
    if [ -d "dist/yiQGuard.app" ]; then
        echo "✅ 打包完成！"
        echo "   大小: $(du -sh dist/yiQGuard.app | cut -f1)"
        echo "   安装: cp -r dist/yiQGuard.app /Applications/"
        echo "   运行: open /Applications/yiQGuard.app"
    else
        echo "❌ 打包失败"
        echo ""
        echo "排查："
        echo "  1. 先试: bash build.sh --alias"
        echo "  2. brew install libffi"
        echo "  3. xcode-select --install"
        exit 1
    fi
fi

echo ""
echo "───────────────────────────────────────────"
echo "  首次运行需授权: 系统设置 → 辅助功能"
echo "───────────────────────────────────────────"
