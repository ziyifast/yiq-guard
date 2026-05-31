import queue
import threading

import Quartz

# Cmd+Q 的 keyCode 和 modifier flags
_CMD_Q_KEYCODE = 12  # Q 键
_CMD_FLAG = Quartz.kCGEventFlagMaskCommand
_ALT_FLAG = Quartz.kCGEventFlagMaskAlternate   # Option
_SHIFT_FLAG = Quartz.kCGEventFlagMaskShift
_CTRL_FLAG = Quartz.kCGEventFlagMaskControl

# Cmd+Q 需要排除的组合键（防止误判 Cmd+Shift+Q 等）
_CMD_Q_IGNORE = _SHIFT_FLAG | _CTRL_FLAG | _ALT_FLAG

# kCGEventTapDisabledByTimeout / ByUserInput 是特殊值（0xFFFFFFFE / 0xFFFFFFFF）
# 不能放进 CGEventMaskBit（会溢出），只能在回调里直接比较
_TAP_DISABLED_BY_TIMEOUT = 0xFFFFFFFE
_TAP_DISABLED_BY_USER_INPUT = 0xFFFFFFFF

# event mask：只监听普通键盘按下事件
_EVENT_MASK = Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)

# macOS keycode 映射（常用字母键）
_KEYCODE_MAP = {
    "a": 0, "b": 11, "c": 8, "d": 2, "e": 14, "f": 3, "g": 5,
    "h": 4, "i": 34, "j": 38, "k": 40, "l": 37, "m": 46, "n": 45,
    "o": 31, "p": 35, "q": 12, "r": 15, "s": 1, "t": 17, "u": 32,
    "v": 9, "w": 13, "x": 7, "y": 16, "z": 6,
}


def _build_hotkey_flags(hotkey_config):
    """根据配置构建 modifier flags 和 keycode。"""
    flags = 0
    if hotkey_config.get("ctrl"):
        flags |= _CTRL_FLAG
    if hotkey_config.get("option"):
        flags |= _ALT_FLAG
    if hotkey_config.get("shift"):
        flags |= _SHIFT_FLAG
    if hotkey_config.get("cmd"):
        flags |= _CMD_FLAG

    key = hotkey_config.get("key", "q").lower()
    keycode = _KEYCODE_MAP.get(key, 12)  # 默认 Q

    return flags, keycode


class EventTap:
    """
    在独立线程上运行 CGEventTap，拦截系统级键盘事件：
      - Cmd+Q              → 发送 "cmd_q" 到队列（吞掉原始事件）
      - 设置快捷键（可配置）→ 发送 "open_settings" 到队列（吞掉原始事件）

    关键设计：
    - 回调函数极简，只做 queue.put_nowait，绝不阻塞
    - 检测 kCGEventTapDisabledByTimeout，超时后立即重启 tap
    - 避免 PyObjC GIL 竞争导致键盘卡死
    """

    def __init__(self, hotkey_config=None, quit_hotkey_config=None):
        self._tap = None
        self._run_loop_source = None
        self._thread = None
        self._run_loop = None
        self._started = threading.Event()
        self._running = False
        self.event_queue = queue.Queue()

        # 设置快捷键配置，默认 Ctrl+Option+Q
        if hotkey_config is None:
            hotkey_config = {"ctrl": True, "option": True, "shift": False, "key": "q"}
        self._hotkey_flags, self._hotkey_keycode = _build_hotkey_flags(hotkey_config)

        # 退出快捷键配置，默认 Ctrl+Option+Shift+Q
        if quit_hotkey_config is None:
            quit_hotkey_config = {"ctrl": True, "option": True, "shift": True, "key": "q"}
        self._quit_hotkey_flags, self._quit_hotkey_keycode = _build_hotkey_flags(quit_hotkey_config)

    def start(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="EventTapThread"
        )
        self._thread.start()
        self._started.wait(timeout=3.0)

    def stop(self):
        self._running = False
        if self._tap:
            Quartz.CGEventTapEnable(self._tap, False)
        if self._run_loop:
            Quartz.CFRunLoopStop(self._run_loop)
        if self._thread:
            self._thread.join(timeout=2.0)
        self._tap = None
        self._run_loop_source = None
        self._run_loop = None

    def is_running(self) -> bool:
        """返回 tap 是否处于活跃状态（线程在跑且 tap 句柄存在）。"""
        return self._running and self._tap is not None

    def _run(self):
        event_queue = self.event_queue
        tap_ref = [None]  # 让回调内可访问 tap 句柄
        hotkey_flags = self._hotkey_flags
        hotkey_keycode = self._hotkey_keycode
        quit_hotkey_flags = self._quit_hotkey_flags
        quit_hotkey_keycode = self._quit_hotkey_keycode

        def _callback(proxy, event_type, event, refcon):
            # tap 被系统超时禁用 → 立即重新启用
            if event_type in (_TAP_DISABLED_BY_TIMEOUT, _TAP_DISABLED_BY_USER_INPUT):
                if tap_ref[0]:
                    Quartz.CGEventTapEnable(tap_ref[0], True)
                return event

            if event_type == Quartz.kCGEventKeyDown:
                keycode = Quartz.CGEventGetIntegerValueField(
                    event, Quartz.kCGKeyboardEventKeycode
                )
                flags = Quartz.CGEventGetFlags(event)
                modifier_mask = _CMD_FLAG | _ALT_FLAG | _SHIFT_FLAG | _CTRL_FLAG

                # 退出快捷键 → 发送 "quit_app" 到队列
                if keycode == quit_hotkey_keycode:
                    if (flags & modifier_mask) == quit_hotkey_flags:
                        try:
                            event_queue.put_nowait("quit_app")
                        except queue.Full:
                            pass
                        return None

                # 设置快捷键 → 打开设置窗口
                if keycode == hotkey_keycode:
                    if (flags & modifier_mask) == hotkey_flags:
                        try:
                            event_queue.put_nowait("open_settings")
                        except queue.Full:
                            pass
                        return None

                # Cmd+Q（不含 Shift/Ctrl/Alt）→ 保护拦截
                if keycode == _CMD_Q_KEYCODE:
                    if (flags & _CMD_FLAG) and not (flags & _CMD_Q_IGNORE):
                        try:
                            event_queue.put_nowait("cmd_q")
                        except queue.Full:
                            pass
                        return None

            return event

        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            _EVENT_MASK,
            _callback,
            None,
        )
        if not tap:
            print("[EventTap] 创建失败：请检查辅助功能权限")
            self._started.set()
            return

        tap_ref[0] = tap
        self._tap = tap

        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        self._run_loop_source = run_loop_source
        self._run_loop = Quartz.CFRunLoopGetCurrent()

        Quartz.CFRunLoopAddSource(
            self._run_loop,
            run_loop_source,
            Quartz.kCFRunLoopCommonModes,
        )
        Quartz.CGEventTapEnable(tap, True)
        self._started.set()

        Quartz.CFRunLoopRun()

        Quartz.CFRunLoopRemoveSource(
            self._run_loop,
            run_loop_source,
            Quartz.kCFRunLoopCommonModes,
        )
