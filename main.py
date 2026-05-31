import sys
import os

# 开发模式下确保项目根目录在模块搜索路径中
# 打包为 .app 后 py2app 会自动处理路径，此行无害
if not getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Cocoa import NSApplication, NSApplicationActivationPolicyAccessory

from yiqguard.app_delegate import AppDelegate
from yiqguard import config as cfg
from yiqguard import permissions


def main():
    # 支持命令行快速切换模式：
    #   python main.py --mode double_press
    #   python main.py --mode confirm
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]
            if mode in ("confirm", "double_press"):
                conf = cfg.load()
                conf["mode"] = mode
                cfg.save(conf)
                print(f"[yiQGuard] 模式已切换为: {mode}")
            else:
                print(f"[yiQGuard] 无效模式: {mode}（可选: confirm, double_press）")
                sys.exit(1)

    app = NSApplication.sharedApplication()

    # 隐藏 Dock 图标（纯菜单栏工具）
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    # 检查辅助功能权限，未授权时弹出系统引导
    if not permissions.is_trusted(prompt=True):
        print(
            "[yiQGuard] 需要辅助功能权限。\n"
            "请前往「系统设置 → 隐私与安全性 → 辅助功能」授权后重新启动。"
        )
        sys.exit(1)

    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


if __name__ == "__main__":
    main()
