"""
py2app 打包配置
用法：
    pip install py2app
    python setup.py py2app
生成的 .app 在 dist/ 目录下。

常见问题：
    - 如果打包后 Launch error，先尝试: python setup.py py2app -A（别名模式快速测试）
    - 确保 libffi 已安装: brew install libffi
    - 确保在 venv 中打包（避免 conda 环境干扰）
"""
import os
import subprocess
from setuptools import setup


def find_libffi():
    """自动查找 libffi.8.dylib 路径。"""
    candidates = [
        "/opt/homebrew/lib/libffi.8.dylib",       # Apple Silicon Homebrew
        "/usr/local/lib/libffi.8.dylib",           # Intel Homebrew
        "/opt/homebrew/opt/libffi/lib/libffi.8.dylib",
        "/usr/local/opt/libffi/lib/libffi.8.dylib",
        # Xcode Command Line Tools
        "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib/libffi.dylib",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # 用 find 兜底
    try:
        result = subprocess.check_output(
            ["find", "/opt/homebrew", "/usr/local", "-name", "libffi*.dylib", "-type", "f"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode().strip()
        if result:
            # 优先选 libffi.8.dylib
            for line in result.splitlines():
                if "libffi.8" in line:
                    return line
            return result.splitlines()[0]
    except Exception:
        pass
    return None


APP = ["main.py"]

libffi_path = find_libffi()
frameworks = []
if libffi_path:
    print(f"[setup.py] 找到 libffi: {libffi_path}")
    frameworks.append(libffi_path)
else:
    print("[setup.py] 警告：未找到 libffi，尝试不打包（系统自带可能可用）")
    print("          如果打包后 Launch error，请运行: brew install libffi")

# 检查 icon.icns 是否存在
icon_file = "icon.icns" if os.path.exists("icon.icns") else None
if not icon_file:
    print("[setup.py] 提示：未找到 icon.icns，将使用默认图标")

OPTIONS = {
    "argv_emulation": False,
    "iconfile": icon_file,
    "frameworks": frameworks if frameworks else None,
    "plist": {
        "CFBundleName": "yiQGuard",
        "CFBundleDisplayName": "yiQGuard",
        "CFBundleIdentifier": "com.ziyi.yiqguard",
        "CFBundleVersion": "1.1.0",
        "CFBundleShortVersionString": "1.1",
        "LSUIElement": True,
        "NSPrincipalClass": "NSApplication",
        "NSHighResolutionCapable": True,
        "NSAppleEventsUsageDescription": "yiQGuard 需要辅助功能权限以拦截 Cmd+Q 事件。",
    },
    "packages": ["yiqguard"],
    "includes": [
        "AppKit",
        "Cocoa",
        "Foundation",
        "Quartz",
        "ApplicationServices",
        "objc",
        "ctypes",
        "ctypes.util",
        "queue",
        "threading",
        "signal",
        "json",
        "tempfile",
        "time",
    ],
}

# 移除 None 值
OPTIONS = {k: v for k, v in OPTIONS.items() if v is not None}

setup(
    name="yiQGuard",
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
