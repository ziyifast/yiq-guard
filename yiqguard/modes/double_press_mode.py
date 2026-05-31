"""
双击 Cmd+Q 模式：
- 第一次按下：记录时间和当时的前台应用，调用 on_first_press(app_name) 显示提示
- 0.8s 内第二次按下：退出第一次记录的应用（不重新获取，避免 Toast 抢焦点导致对象错误）
- 超时后重置
"""
import time

from AppKit import NSWorkspace

DOUBLE_PRESS_INTERVAL = 1.5


class DoublePressMode:
    def __init__(self):
        self._last_press_time = 0.0
        self._target_app = None  # 第一次按下时记录的目标应用

    def handle(self, on_quit, on_first_press=None):
        """
        必须在主线程调用。
        on_quit(app)         接收 NSRunningApplication，执行退出。
        on_first_press(name) 接收应用名字符串，用于显示提示（可选）。
        """
        now = time.time()
        elapsed = now - self._last_press_time

        if elapsed <= DOUBLE_PRESS_INTERVAL and self._target_app is not None:
            # 第二次按下：用第一次记录的 app 退出，不重新获取 frontmost
            app = self._target_app
            self._last_press_time = 0.0
            self._target_app = None
            on_quit(app)
        else:
            # 第一次按下：记录时间和当前前台应用
            workspace = NSWorkspace.sharedWorkspace()
            frontmost_app = workspace.frontmostApplication()
            self._last_press_time = now
            self._target_app = frontmost_app
            if on_first_press is not None:
                app_name = frontmost_app.localizedName() if frontmost_app else ""
                on_first_press(app_name)

    def reset(self):
        self._last_press_time = 0.0
        self._target_app = None
