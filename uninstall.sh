#!/bin/bash
# yiQGuard 卸载脚本
# 用法：bash uninstall.sh

echo "═══════════════════════════════════════════"
echo "  yiQGuard 卸载工具"
echo "═══════════════════════════════════════════"
echo ""

REMOVED=0

# ── 关闭运行中的 yiQGuard ─────────────────────────────────────
if pgrep -f "yiQGuard" >/dev/null 2>&1; then
    echo "  正在关闭 yiQGuard 进程..."
    pkill -f "yiQGuard" 2>/dev/null || true
    sleep 1
    echo "  ✓ 已关闭"
    REMOVED=1
fi

# ── 删除 .app ────────────────────────────────────────────────
if [ -d "/Applications/yiQGuard.app" ]; then
    echo "  删除 /Applications/yiQGuard.app..."
    rm -rf "/Applications/yiQGuard.app"
    echo "  ✓ 已删除"
    REMOVED=1
fi

# 也检查当前目录的 dist
if [ -d "dist/yiQGuard.app" ]; then
    echo "  删除 dist/yiQGuard.app..."
    rm -rf dist/
    echo "  ✓ 已删除"
    REMOVED=1
fi

# ── 删除配置文件 ──────────────────────────────────────────────
CONFIG_DIR="$HOME/.yiq-guard"
if [ -d "$CONFIG_DIR" ]; then
    echo "  删除配置目录 $CONFIG_DIR..."
    rm -rf "$CONFIG_DIR"
    echo "  ✓ 已删除"
    REMOVED=1
else
    echo "  ✓ 无配置文件"
fi

# ── 从登录项移除（提示用户手动操作）─────────────────────────────
echo ""
if [ $REMOVED -gt 0 ]; then
    echo "✅ yiQGuard 已卸载"
else
    echo "ℹ️  未找到 yiQGuard 安装"
fi

echo ""
echo "───────────────────────────────────────────"
echo "  请手动完成以下步骤："
echo ""
echo "  1. 移除辅助功能权限："
echo "     系统设置 → 隐私与安全性 → 辅助功能"
echo "     → 找到 yiQGuard → 取消勾选或删除"
echo ""
echo "  2. 移除登录项（如已设置）："
echo "     系统设置 → 通用 → 登录项"
echo "     → 找到 yiQGuard → 移除"
echo "───────────────────────────────────────────"
echo ""
echo "感谢使用 yiQGuard！"
