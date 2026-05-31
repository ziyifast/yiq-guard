#!/bin/bash
# yiQGuard 发布打包脚本
# 生成可分发的 .zip 文件，用于上传到 GitHub Release
#
# 用法：bash release.sh
# 输出：release/yiQGuard-v1.1.0-macOS.zip

set -e

VERSION="1.1.0"
RELEASE_DIR="release"
APP_NAME="yiQGuard"
ZIP_NAME="${APP_NAME}-v${VERSION}-macOS.zip"

echo "═══════════════════════════════════════════"
echo "  yiQGuard v${VERSION} 发布打包"
echo "═══════════════════════════════════════════"
echo ""

# 先执行正式打包
bash build.sh

if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ 打包失败，无法生成发布文件"
    exit 1
fi

# 创建 release 目录
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# 签名（使用 ad-hoc 签名，非 App Store 分发）
echo "签名 .app..."
codesign --deep --force --sign "-" "dist/${APP_NAME}.app" 2>/dev/null || true

# 压缩为 .zip
echo "压缩为 ${ZIP_NAME}..."
cd dist
zip -r -q "../${RELEASE_DIR}/${ZIP_NAME}" "${APP_NAME}.app"
cd ..

# 生成 SHA256
SHA256=$(shasum -a 256 "${RELEASE_DIR}/${ZIP_NAME}" | cut -d' ' -f1)

echo ""
echo "✅ 发布文件已生成！"
echo ""
echo "   文件: ${RELEASE_DIR}/${ZIP_NAME}"
echo "   大小: $(du -sh "${RELEASE_DIR}/${ZIP_NAME}" | cut -f1)"
echo "   SHA256: ${SHA256}"
echo ""
echo "───────────────────────────────────────────"
echo "  上传到 GitHub Release："
echo ""
echo "  gh release create v${VERSION} ${RELEASE_DIR}/${ZIP_NAME} \\"
echo "    --title \"v${VERSION}\" \\"
echo "    --notes \"## 安装"
echo ""
echo "  1. 下载 ${ZIP_NAME}"
echo "  2. 解压后将 yiQGuard.app 拖入 /Applications"
echo "  3. 首次打开需右键 → 打开（绕过 Gatekeeper）"
echo "  4. 授权辅助功能权限\""
echo "───────────────────────────────────────────"
