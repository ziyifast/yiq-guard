"""独立设置窗口（NSPanel），点击菜单栏图标或按 Ctrl+Option+Q 时打开。"""
import objc
from Cocoa import (
    NSObject,
    NSApp,
    NSPanel,
    NSButton,
    NSTextField,
    NSColor,
    NSFont,
    NSMakeRect,
    NSWindowStyleMaskTitled,
    NSWindowStyleMaskClosable,
    NSBackingStoreBuffered,
    NSTextAlignmentCenter,
    NSTextAlignmentLeft,
    NSFloatingWindowLevel,
)

from yiqguard import config as cfg

# NSWindowStyleMaskNonactivatingPanel 在部分版本常量名不同，安全获取
try:
    from Cocoa import NSWindowStyleMaskNonactivatingPanel
    _NONACTIVATING = NSWindowStyleMaskNonactivatingPanel
except ImportError:
    _NONACTIVATING = 1 << 7  # 数值等价

# NSSwitchButton 常量值固定为 3
_SWITCH_BUTTON = 3


class _WindowDelegate(NSObject):
    """捕获窗口关闭事件，通知 SettingsWindow。"""

    def initWithOwner_(self, owner):
        self = objc.super(_WindowDelegate, self).init()
        if self is not None:
            self._owner = owner
        return self

    def windowWillClose_(self, notification):
        self._owner._on_window_close()


class _ButtonHandler(NSObject):
    """处理按钮点击事件。"""

    def initWithWindow_(self, settings_win):
        self = objc.super(_ButtonHandler, self).init()
        if self is not None:
            self._win = settings_win
        return self

    def toggleProtection_(self, sender):
        self._win._toggle_protection()

    def setModeConfirm_(self, sender):
        self._win._set_mode("confirm")

    def setModeDouble_(self, sender):
        self._win._set_mode("double_press")

    def saveHotkeys_(self, sender):
        self._win._save_hotkeys()


class SettingsWindow:
    """
    独立的悬浮设置面板：
      - 保护开关（checkbox）
      - 模式选择（两个按钮，高亮当前模式）
      - 快捷键自定义（修饰键 checkbox + 字母输入）
    打开方式：点击菜单栏图标 → "打开设置…" 或按 Ctrl+Option+Q
    """

    _W = 340
    _H = 380

    def __init__(self, config, on_toggle, on_mode_change):
        self._config = config
        self._on_toggle = on_toggle
        self._on_mode_change = on_mode_change
        self._panel = None
        self._toggle_btn = None
        self._confirm_btn = None
        self._double_btn = None
        self._handler = _ButtonHandler.alloc().initWithWindow_(self)
        self._delegate = _WindowDelegate.alloc().initWithOwner_(self)

        # 快捷键 UI 控件
        self._settings_ctrl_cb = None
        self._settings_opt_cb = None
        self._settings_shift_cb = None
        self._settings_key_field = None
        self._quit_ctrl_cb = None
        self._quit_opt_cb = None
        self._quit_shift_cb = None
        self._quit_key_field = None

    # ── 公共接口 ──────────────────────────────────────────────

    def show(self):
        """打开/显示设置窗口（若已存在则直接显示）。"""
        if self._panel is None:
            self._build_panel()
        self._refresh()
        NSApp.activateIgnoringOtherApps_(True)
        self._panel.makeKeyAndOrderFront_(None)

    def refresh(self):
        """外部调用：刷新窗口内显示状态（config 已更新时）。"""
        if self._panel is not None:
            self._refresh()

    # ── 构建 UI ───────────────────────────────────────────────

    def _build_panel(self):
        w, h = self._W, self._H

        style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | _NONACTIVATING
        self._panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, w, h),
            style,
            NSBackingStoreBuffered,
            False,
        )
        self._panel.setTitle_("yiQGuard 设置")
        self._panel.setLevel_(NSFloatingWindowLevel)
        self._panel.setDelegate_(self._delegate)
        self._panel.center()

        cv = self._panel.contentView()
        y = h - 40  # 从顶部开始布局

        # ── 标题 ──────────────────────────────────────────────
        self._add_label(cv, "🛡 yiQGuard 防误触设置",
                        NSMakeRect(20, y, w - 40, 24),
                        font=NSFont.boldSystemFontOfSize_(14),
                        color=NSColor.labelColor(),
                        align=NSTextAlignmentCenter)
        y -= 30
        self._add_separator(cv, NSMakeRect(20, y, w - 40, 1))
        y -= 35

        # ── 保护开关 ─────────────────────────────────────────
        self._toggle_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, y, w - 40, 24))
        self._toggle_btn.setButtonType_(_SWITCH_BUTTON)
        self._toggle_btn.setTitle_("  启用 Cmd+Q 保护")
        self._toggle_btn.setFont_(NSFont.systemFontOfSize_(13))
        self._toggle_btn.setTarget_(self._handler)
        self._toggle_btn.setAction_("toggleProtection:")
        cv.addSubview_(self._toggle_btn)
        y -= 30

        # ── 模式选择 ─────────────────────────────────────────
        self._add_label(cv, "保护模式：",
                        NSMakeRect(20, y, w - 40, 18),
                        font=NSFont.systemFontOfSize_(12),
                        color=NSColor.secondaryLabelColor(),
                        align=NSTextAlignmentLeft)
        y -= 28

        self._confirm_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, y, 130, 26))
        self._confirm_btn.setTitle_("弹窗确认")
        self._confirm_btn.setBezelStyle_(1)
        self._confirm_btn.setTarget_(self._handler)
        self._confirm_btn.setAction_("setModeConfirm:")
        cv.addSubview_(self._confirm_btn)

        self._double_btn = NSButton.alloc().initWithFrame_(NSMakeRect(160, y, 155, 26))
        self._double_btn.setTitle_("双击 Cmd+Q (1.5s)")
        self._double_btn.setBezelStyle_(1)
        self._double_btn.setTarget_(self._handler)
        self._double_btn.setAction_("setModeDouble:")
        cv.addSubview_(self._double_btn)
        y -= 30

        self._add_separator(cv, NSMakeRect(20, y, w - 40, 1))
        y -= 25

        # ── 快捷键配置：打开设置 ─────────────────────────────
        self._add_label(cv, "打开设置快捷键：",
                        NSMakeRect(20, y, w - 40, 18),
                        font=NSFont.systemFontOfSize_(12),
                        color=NSColor.secondaryLabelColor(),
                        align=NSTextAlignmentLeft)
        y -= 24

        settings_hk = self._config.get("settings_hotkey", cfg.DEFAULTS["settings_hotkey"])
        self._settings_ctrl_cb = self._add_checkbox(cv, "Ctrl", NSMakeRect(20, y, 55, 20), settings_hk.get("ctrl", False))
        self._settings_opt_cb = self._add_checkbox(cv, "Opt", NSMakeRect(80, y, 50, 20), settings_hk.get("option", False))
        self._settings_shift_cb = self._add_checkbox(cv, "Shift", NSMakeRect(135, y, 60, 20), settings_hk.get("shift", False))

        self._add_label(cv, "+", NSMakeRect(198, y, 15, 18),
                        font=NSFont.systemFontOfSize_(12),
                        color=NSColor.labelColor(),
                        align=NSTextAlignmentCenter)

        self._settings_key_field = NSTextField.alloc().initWithFrame_(NSMakeRect(218, y, 35, 22))
        self._settings_key_field.setStringValue_(settings_hk.get("key", "q").upper())
        self._settings_key_field.setFont_(NSFont.systemFontOfSize_(12))
        self._settings_key_field.setAlignment_(NSTextAlignmentCenter)
        cv.addSubview_(self._settings_key_field)
        y -= 30

        # ── 快捷键配置：退出 yiQGuard ────────────────────────
        self._add_label(cv, "退出 yiQGuard 快捷键：",
                        NSMakeRect(20, y, w - 40, 18),
                        font=NSFont.systemFontOfSize_(12),
                        color=NSColor.secondaryLabelColor(),
                        align=NSTextAlignmentLeft)
        y -= 24

        quit_hk = self._config.get("quit_hotkey", cfg.DEFAULTS["quit_hotkey"])
        self._quit_ctrl_cb = self._add_checkbox(cv, "Ctrl", NSMakeRect(20, y, 55, 20), quit_hk.get("ctrl", False))
        self._quit_opt_cb = self._add_checkbox(cv, "Opt", NSMakeRect(80, y, 50, 20), quit_hk.get("option", False))
        self._quit_shift_cb = self._add_checkbox(cv, "Shift", NSMakeRect(135, y, 60, 20), quit_hk.get("shift", False))

        self._add_label(cv, "+", NSMakeRect(198, y, 15, 18),
                        font=NSFont.systemFontOfSize_(12),
                        color=NSColor.labelColor(),
                        align=NSTextAlignmentCenter)

        self._quit_key_field = NSTextField.alloc().initWithFrame_(NSMakeRect(218, y, 35, 22))
        self._quit_key_field.setStringValue_(quit_hk.get("key", "q").upper())
        self._quit_key_field.setFont_(NSFont.systemFontOfSize_(12))
        self._quit_key_field.setAlignment_(NSTextAlignmentCenter)
        cv.addSubview_(self._quit_key_field)
        y -= 32

        # ── 保存快捷键按钮 ───────────────────────────────────
        save_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, y, w - 40, 26))
        save_btn.setTitle_("保存快捷键（重启后生效）")
        save_btn.setBezelStyle_(1)
        save_btn.setTarget_(self._handler)
        save_btn.setAction_("saveHotkeys:")
        cv.addSubview_(save_btn)
        y -= 25

        self._add_separator(cv, NSMakeRect(20, y, w - 40, 1))
        y -= 5

        # ── 底部提示 ─────────────────────────────────────────
        self._add_label(
            cv,
            "修改快捷键后需重启 yiQGuard 生效\n"
            "快捷键至少选择一个修饰键 + 一个字母键",
            NSMakeRect(20, 5, w - 40, 30),
            font=NSFont.systemFontOfSize_(10),
            color=NSColor.tertiaryLabelColor(),
            align=NSTextAlignmentCenter,
        )

    def _add_checkbox(self, parent, title, rect, checked):
        """创建一个 checkbox 并返回。"""
        cb = NSButton.alloc().initWithFrame_(rect)
        cb.setButtonType_(_SWITCH_BUTTON)
        cb.setTitle_(title)
        cb.setFont_(NSFont.systemFontOfSize_(11))
        cb.setState_(1 if checked else 0)
        parent.addSubview_(cb)
        return cb

    @staticmethod
    def _add_label(parent, text, rect, font, color, align):
        lbl = NSTextField.alloc().initWithFrame_(rect)
        lbl.setStringValue_(text)
        lbl.setFont_(font)
        lbl.setTextColor_(color)
        lbl.setEditable_(False)
        lbl.setBordered_(False)
        lbl.setDrawsBackground_(False)
        lbl.setAlignment_(align)
        parent.addSubview_(lbl)
        return lbl

    @staticmethod
    def _add_separator(parent, rect):
        sep = NSTextField.alloc().initWithFrame_(rect)
        sep.setDrawsBackground_(True)
        sep.setBackgroundColor_(NSColor.separatorColor())
        sep.setBordered_(False)
        sep.setEditable_(False)
        parent.addSubview_(sep)

    # ── 刷新状态 ──────────────────────────────────────────────

    def _refresh(self):
        if self._toggle_btn is None:
            return
        enabled = self._config.get("enabled", True)
        mode = self._config.get("mode", "double_press")

        self._toggle_btn.setState_(1 if enabled else 0)

        if mode == "confirm":
            self._confirm_btn.setKeyEquivalent_("\r")
            self._double_btn.setKeyEquivalent_("")
        else:
            self._confirm_btn.setKeyEquivalent_("")
            self._double_btn.setKeyEquivalent_("\r")

        self._confirm_btn.setEnabled_(enabled)
        self._double_btn.setEnabled_(enabled)

    # ── 内部回调 ──────────────────────────────────────────────

    def _toggle_protection(self):
        self._on_toggle()
        self._refresh()

    def _set_mode(self, mode):
        self._on_mode_change(mode)
        self._refresh()

    def _save_hotkeys(self):
        """从 UI 读取快捷键配置并保存到 config。"""
        # 读取设置快捷键
        settings_hotkey = {
            "ctrl": bool(self._settings_ctrl_cb.state()),
            "option": bool(self._settings_opt_cb.state()),
            "shift": bool(self._settings_shift_cb.state()),
            "key": str(self._settings_key_field.stringValue()).strip().lower()[:1] or "q",
        }

        # 读取退出快捷键
        quit_hotkey = {
            "ctrl": bool(self._quit_ctrl_cb.state()),
            "option": bool(self._quit_opt_cb.state()),
            "shift": bool(self._quit_shift_cb.state()),
            "key": str(self._quit_key_field.stringValue()).strip().lower()[:1] or "q",
        }

        # 验证：至少要有一个修饰键
        for name, hk in [("设置", settings_hotkey), ("退出", quit_hotkey)]:
            if not (hk["ctrl"] or hk["option"] or hk["shift"]):
                from yiqguard.ui.toast import Toast
                Toast().show(f"❌ {name}快捷键至少需要一个修饰键", duration=2.0)
                return

        self._config["settings_hotkey"] = settings_hotkey
        self._config["quit_hotkey"] = quit_hotkey
        cfg.save(self._config)

        from yiqguard.ui.toast import Toast
        Toast().show("✅ 快捷键已保存，重启 yiQGuard 后生效", duration=2.0)

    def _on_window_close(self):
        self._panel = None
        self._toggle_btn = None
        self._confirm_btn = None
        self._double_btn = None
        self._settings_ctrl_cb = None
        self._settings_opt_cb = None
        self._settings_shift_cb = None
        self._settings_key_field = None
        self._quit_ctrl_cb = None
        self._quit_opt_cb = None
        self._quit_shift_cb = None
        self._quit_key_field = None
