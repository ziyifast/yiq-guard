import queue
import signal
import threading

import Quartz
from Cocoa import NSApp, NSObject, NSAlert, NSAlertFirstButtonReturn
from Foundation import NSTimer

from yiqguard import config as cfg
from yiqguard import permissions
from yiqguard.event_tap import EventTap
from yiqguard.modes.confirm_mode import handle as confirm_handle
from yiqguard.modes.double_press_mode import DoublePressMode
from yiqguard.ui.menu_bar import MenuBar
from yiqguard.ui.settings_window import SettingsWindow
from yiqguard.ui.toast import Toast

# 权限检查间隔（秒）
_PERM_CHECK_INTERVAL = 3.0


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        self._config = cfg.load()
        self._config_lock = threading.Lock()

        self._double_press = DoublePressMode()
        self._toast = Toast()

        self._settings_win = SettingsWindow(
            config=self._config,
            on_toggle=self._toggle,
            on_mode_change=self._set_mode,
        )

        self._menu_bar = MenuBar(
            config=self._config,
            on_toggle=self._toggle,
            on_mode_change=self._set_mode,
            on_quit_app=self._quit_app,
            on_open_settings=self._open_settings,
        )
        self._menu_bar.setup()

        self._tap = EventTap(
            hotkey_config=self._config.get("settings_hotkey"),
            quit_hotkey_config=self._config.get("quit_hotkey"),
        )
        self._tap.start()

        # 每 20ms 轮询事件队列
        self._poll_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.02, self, "pollQueue:", None, True
        )

        # 每 3s 检查辅助功能权限，权限丢失时立刻停止 tap 防键盘卡死
        self._perm_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            _PERM_CHECK_INTERVAL, self, "checkPermissions:", None, True
        )

        signal.signal(signal.SIGINT, signal.SIG_IGN)  # 忽略 Ctrl+C，防止意外退出

        # 启动成功通知
        self._show_launch_toast()

    def _show_launch_toast(self):
        """启动时显示 Toast 通知，让用户感知 yiQGuard 已激活。"""
        mode = self._config.get("mode", "double_press")
        if mode == "double_press":
            mode_text = "双击 Cmd+Q 退出"
        else:
            mode_text = "弹窗确认退出"
        self._toast.show(f"🛡 yiQGuard 已启动 — {mode_text}", duration=2.5)

    def pollQueue_(self, timer):
        try:
            while True:
                msg = self._tap.event_queue.get_nowait()
                if msg == "open_settings":
                    self._open_settings()
                    continue
                if msg == "quit_app":
                    self._quit_app()
                    continue
                with self._config_lock:
                    enabled = self._config["enabled"]
                if msg == "cmd_q" and enabled:
                    self._handle_cmd_q()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"[AppDelegate] pollQueue 异常: {e}")

    def checkPermissions_(self, timer):
        """
        定期检查辅助功能权限。
        权限丢失时立刻停止 EventTap，防止键盘被卡死。
        """
        if not permissions.is_trusted(prompt=False):
            if self._tap and self._tap.is_running():
                print("[AppDelegate] 辅助功能权限已撤销，停止事件拦截")
                self._tap.stop()
                self._show_permission_lost_alert()

    def _show_permission_lost_alert(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("yiQGuard 已暂停保护")
        alert.setInformativeText_(
            "辅助功能权限已被撤销，键盘拦截已停止。\n\n"
            "如需恢复保护，请在「系统设置 → 隐私与安全性 → 辅助功能」"
            "中重新勾选 yiQGuard，然后重启应用。"
        )
        alert.addButtonWithTitle_("知道了")
        alert.runModal()

    def _handle_cmd_q(self):
        """
        处理 Cmd+Q 事件。
        yiQGuard 自身不可通过 Cmd+Q 退出（直接忽略）。
        其他应用走双击/确认保护。
        """
        from AppKit import NSWorkspace

        # 检查当前前台应用是否是 yiQGuard 自身 → 直接忽略，不退出
        workspace = NSWorkspace.sharedWorkspace()
        frontmost = workspace.frontmostApplication()
        if frontmost:
            bundle_id = frontmost.bundleIdentifier()
            if bundle_id and "yiqguard" in str(bundle_id).lower():
                # yiQGuard 自身：忽略 Cmd+Q，显示提示
                self._toast.show("🛡 yiQGuard 不可通过 Cmd+Q 退出\n如需退出请使用「强制退出」(⌘⌥Esc)", duration=2.0)
                NSApp.hide_(None)  # 隐藏自身，焦点回到上一个应用
                return

        with self._config_lock:
            mode = self._config.get("mode", "double_press")
        if mode == "confirm":
            confirm_handle(on_quit=self._do_quit_app)
        else:
            self._double_press.handle(
                on_quit=self._do_quit_app,
                on_first_press=self._show_double_press_hint,
            )

    def _show_double_press_hint(self, app_name: str):
        if app_name:
            msg = f"再按一次 Cmd+Q 退出「{app_name}」"
        else:
            msg = "再按一次 Cmd+Q 即可退出应用"
        self._toast.show(msg, duration=1.5)

    def _do_quit_app(self, running_app):
        """退出目标应用。yiQGuard 自身永远不会被这个方法退出。"""
        if running_app:
            bundle_id = running_app.bundleIdentifier()
            # 再次防护：永远不退出 yiQGuard 自身
            if bundle_id and "yiqguard" in str(bundle_id).lower():
                return
            running_app.terminate()

    def _toggle(self):
        with self._config_lock:
            self._config["enabled"] = not self._config["enabled"]
            enabled = self._config["enabled"]
        if not enabled:
            self._double_press.reset()
        cfg.save(self._config)

    def _set_mode(self, mode):
        with self._config_lock:
            self._config["mode"] = mode
        self._double_press.reset()
        cfg.save(self._config)

    def _open_settings(self):
        self._settings_win.show()

    def _quit_app(self):
        """退出 yiQGuard：弹出 Critical 确认弹窗。"""
        from Cocoa import NSFloatingWindowLevel, NSCriticalAlertStyle

        alert = NSAlert.alloc().init()
        alert.setAlertStyle_(NSCriticalAlertStyle)
        alert.setMessageText_("⚠️ 确定退出 yiQGuard？")
        alert.setInformativeText_(
            "退出后 Cmd+Q 保护将完全失效！\n\n"
            "所有应用按 Cmd+Q 将直接退出，\n"
            "你的未保存工作可能因误触而丢失。"
        )
        alert.addButtonWithTitle_("取消（保持保护）")
        alert.addButtonWithTitle_("确定退出")
        alert.window().setLevel_(NSFloatingWindowLevel)
        NSApp.activateIgnoringOtherApps_(True)

        result = alert.runModal()
        if result == NSAlertFirstButtonReturn + 1:
            self._do_quit()
        else:
            NSApp.hide_(None)

    def _do_quit(self):
        """真正执行退出。"""
        if self._poll_timer:
            self._poll_timer.invalidate()
        if self._perm_timer:
            self._perm_timer.invalidate()
        if self._tap:
            self._tap.stop()
        NSApp.terminate_(None)
