"""
HUD Toast 提示：屏幕中央显示半透明浮动提示，自动消失。
用于双击模式下第一次按 Cmd+Q 时提示用户。
"""
import objc
from Cocoa import (
    NSObject,
    NSPanel,
    NSTextField,
    NSColor,
    NSFont,
    NSMakeRect,
    NSWindowStyleMaskBorderless,
    NSBackingStoreBuffered,
    NSTextAlignmentCenter,
    NSFloatingWindowLevel,
)
from Foundation import NSTimer

# NSWindowStyleMaskNonactivatingPanel 兜底
try:
    from Cocoa import NSWindowStyleMaskNonactivatingPanel
    _NONACTIVATING = NSWindowStyleMaskNonactivatingPanel
except ImportError:
    _NONACTIVATING = 1 << 7


class _TimerTarget(NSObject):
    """NSTimer 回调目标，持有对 Toast 的弱引用避免循环引用问题。"""

    def initWithToast_(self, toast):
        self = objc.super(_TimerTarget, self).init()
        if self is not None:
            self._toast = toast
        return self

    def dismiss_(self, timer):
        self._toast._dismiss()


class Toast:
    """
    屏幕中央半透明 HUD 提示。
    调用 show(message) 显示，duration 秒后自动消失。
    """

    _W = 360
    _H = 60
    _CORNER_RADIUS = 12.0
    _BG_ALPHA = 0.82

    def __init__(self):
        self._panel = None
        self._timer_target = _TimerTarget.alloc().initWithToast_(self)
        self._auto_timer = None

    def show(self, message: str, duration: float = 1.5):
        """显示提示文字，duration 秒后自动关闭。不抢夺焦点。"""
        # 若已有旧 toast，先取消定时器再复用
        self._cancel_timer()

        if self._panel is None:
            self._build_panel()

        self._label.setStringValue_(message)
        # 用 orderFrontRegardless 而非 makeKeyAndOrderFront，不抢焦点
        # 不调用 NSApp.activateIgnoringOtherApps_，保持原前台应用不变
        self._panel.orderFrontRegardless()

        self._auto_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            duration, self._timer_target, "dismiss:", None, False
        )

    # ── 内部 ──────────────────────────────────────────────────

    def _build_panel(self):
        w, h = self._W, self._H

        # 无边框、半透明浮动面板
        style = NSWindowStyleMaskBorderless | _NONACTIVATING
        self._panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, w, h),
            style,
            NSBackingStoreBuffered,
            False,
        )
        self._panel.setLevel_(NSFloatingWindowLevel + 1)
        self._panel.setOpaque_(False)
        self._panel.setAlphaValue_(self._BG_ALPHA)
        self._panel.setHasShadow_(True)
        self._panel.center()

        # 圆角深色背景
        cv = self._panel.contentView()
        cv.setWantsLayer_(True)
        cv.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.1, 0.1, 0.1, 1.0).CGColor()
        )
        cv.layer().setCornerRadius_(self._CORNER_RADIUS)

        # 文字标签
        self._label = NSTextField.alloc().initWithFrame_(NSMakeRect(16, 0, w - 32, h))
        self._label.setStringValue_("")
        self._label.setFont_(NSFont.boldSystemFontOfSize_(15))
        self._label.setTextColor_(NSColor.whiteColor())
        self._label.setEditable_(False)
        self._label.setBordered_(False)
        self._label.setDrawsBackground_(False)
        self._label.setAlignment_(NSTextAlignmentCenter)
        cv.addSubview_(self._label)

    def _cancel_timer(self):
        if self._auto_timer is not None:
            self._auto_timer.invalidate()
            self._auto_timer = None

    def _dismiss(self):
        self._cancel_timer()
        if self._panel is not None:
            self._panel.orderOut_(None)
