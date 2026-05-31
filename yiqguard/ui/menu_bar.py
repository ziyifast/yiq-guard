import objc
from Cocoa import (
    NSMenu,
    NSMenuItem,
    NSObject,
    NSStatusBar,
    NSVariableStatusItemLength,
)


class _ActionHandler(NSObject):
    """处理菜单栏点击动作的 ObjC 对象，必须定义在模块级别。"""

    def initWithMenuBar_(self, menu_bar):
        self = objc.super(_ActionHandler, self).init()
        if self is not None:
            self._menu_bar = menu_bar
        return self

    def openSettings_(self, sender):
        self._menu_bar._on_open_settings()

    def toggleProtection_(self, sender):
        self._menu_bar._on_toggle()
        self._menu_bar.refresh()

    def setModeConfirm_(self, sender):
        self._menu_bar._on_mode_change("confirm")
        self._menu_bar.refresh()

    def setModeDouble_(self, sender):
        self._menu_bar._on_mode_change("double_press")
        self._menu_bar.refresh()

    def quitApp_(self, sender):
        self._menu_bar._on_quit_app()


class MenuBar:
    def __init__(self, config, on_toggle, on_mode_change, on_quit_app=None, on_open_settings=None):
        self._config = config
        self._on_toggle = on_toggle
        self._on_mode_change = on_mode_change
        self._on_quit_app = on_quit_app or (lambda: None)
        self._on_open_settings = on_open_settings or (lambda: None)

        self._status_item = None
        self._toggle_item = None
        self._mode_confirm_item = None
        self._mode_double_item = None
        self._handler = _ActionHandler.alloc().initWithMenuBar_(self)

    def setup(self):
        bar = NSStatusBar.systemStatusBar()
        self._status_item = bar.statusItemWithLength_(NSVariableStatusItemLength)
        self._status_item.setHighlightMode_(True)
        self._status_item.setToolTip_("yiQGuard - Cmd+Q 防误触保护运行中")
        self._refresh_icon()

        menu = NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)

        # ── 状态标题（不可点击）─────────────────────────────────
        title_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "🛡 yiQGuard 保护中", "", ""
        )
        title_item.setEnabled_(False)
        menu.addItem_(title_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # ── 打开设置窗口 ──────────────────────────────────────
        settings_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "打开设置…", "openSettings:", ""
        )
        settings_item.setTarget_(self._handler)
        settings_item.setEnabled_(True)
        menu.addItem_(settings_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # ── 保护开关 ──────────────────────────────────────────
        self._toggle_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "", "toggleProtection:", ""
        )
        self._toggle_item.setTarget_(self._handler)
        self._toggle_item.setEnabled_(True)
        menu.addItem_(self._toggle_item)
        self._refresh_toggle_label()

        menu.addItem_(NSMenuItem.separatorItem())

        # ── 模式选择标题（不可点击） ───────────────────────────
        mode_title = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "保护模式", "", ""
        )
        mode_title.setEnabled_(False)
        menu.addItem_(mode_title)

        # 模式1：弹窗确认
        self._mode_confirm_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "", "setModeConfirm:", ""
        )
        self._mode_confirm_item.setTarget_(self._handler)
        self._mode_confirm_item.setEnabled_(True)
        menu.addItem_(self._mode_confirm_item)

        # 模式2：双击 Cmd+Q
        self._mode_double_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "", "setModeDouble:", ""
        )
        self._mode_double_item.setTarget_(self._handler)
        self._mode_double_item.setEnabled_(True)
        menu.addItem_(self._mode_double_item)

        self._refresh_mode_labels()

        menu.addItem_(NSMenuItem.separatorItem())

        # ── 退出按钮 ──────────────────────────────────────────
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "退出 yiQGuard（⌃⌥⇧Q）", "quitApp:", ""
        )
        quit_item.setTarget_(self._handler)
        quit_item.setEnabled_(True)
        menu.addItem_(quit_item)

        self._status_item.setMenu_(menu)

    # ── 刷新 UI 状态 ──────────────────────────────────────────

    def _refresh_icon(self):
        """
        设置菜单栏图标。使用「⌘Q」文字确保在所有 macOS 版本可见。
        emoji 在部分系统/分辨率下可能不显示，纯文本更可靠。
        """
        if self._config["enabled"]:
            self._status_item.setTitle_("⌘Q🛡")
        else:
            self._status_item.setTitle_("⌘Q✗")

    def _refresh_toggle_label(self):
        if self._config["enabled"]:
            self._toggle_item.setTitle_("✅  保护已启用（点击关闭）")
        else:
            self._toggle_item.setTitle_("⬜  保护已关闭（点击开启）")

    def _refresh_mode_labels(self):
        mode = self._config["mode"]
        if mode == "confirm":
            self._mode_confirm_item.setTitle_("  ✅  弹窗确认")
            self._mode_double_item.setTitle_("  ⬜  双击 Cmd+Q（1.5s 内）")
        else:
            self._mode_confirm_item.setTitle_("  ⬜  弹窗确认")
            self._mode_double_item.setTitle_("  ✅  双击 Cmd+Q（1.5s 内）")

    def refresh(self):
        self._refresh_icon()
        self._refresh_toggle_label()
        self._refresh_mode_labels()
