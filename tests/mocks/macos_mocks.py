# mock macOS 专属模块，让代码在 Linux 上可导入测试
import sys
from unittest.mock import MagicMock
import types


def install_mocks():
    """安装所有 macOS 框架的 mock，在 import 真实模块前调用。"""

    # ── Quartz ────────────────────────────────────────────────
    quartz = types.ModuleType("Quartz")
    quartz.kCGSessionEventTap = 1
    quartz.kCGHeadInsertEventTap = 0
    quartz.kCGEventTapOptionDefault = 0
    quartz.kCGEventKeyDown = 10
    quartz.kCGEventFlagMaskCommand = 1 << 20
    quartz.kCGEventFlagMaskShift = 1 << 17
    quartz.kCGEventFlagMaskControl = 1 << 18
    quartz.kCGEventFlagMaskAlternate = 1 << 19
    quartz.kCGKeyboardEventKeycode = 9
    quartz.kCGEventSourceStateHIDSystemState = 1
    quartz.kCFRunLoopCommonModes = "kCFRunLoopCommonModes"
    quartz.CGEventMaskBit = lambda t: 1 << t
    quartz.CGEventTapCreate = MagicMock(return_value=MagicMock())
    quartz.CGEventTapEnable = MagicMock()
    quartz.CFMachPortCreateRunLoopSource = MagicMock(return_value=MagicMock())
    quartz.CFRunLoopGetCurrent = MagicMock(return_value=MagicMock())
    quartz.CFRunLoopAddSource = MagicMock()
    quartz.CFRunLoopRemoveSource = MagicMock()
    quartz.CFRunLoopRun = MagicMock()
    quartz.CFRunLoopStop = MagicMock()
    quartz.CGEventGetIntegerValueField = MagicMock(return_value=12)
    quartz.CGEventGetFlags = MagicMock(return_value=1 << 20)
    quartz.CGEventSourceCreate = MagicMock(return_value=MagicMock())
    quartz.CGEventCreateKeyboardEvent = MagicMock(return_value=MagicMock())
    quartz.CGEventSetFlags = MagicMock()
    quartz.CGEventPost = MagicMock()
    sys.modules["Quartz"] = quartz

    # ── objc ──────────────────────────────────────────────────
    objc_mod = types.ModuleType("objc")
    objc_mod.lookUpClass = MagicMock()

    class _NSObjectBase:
        @classmethod
        def alloc(cls):
            return cls()
        def init(self):
            return self

    class _SuperProxy:
        def __init__(self, instance):
            self._instance = instance
        def init(self):
            return self._instance

    objc_mod.super = lambda cls, instance: _SuperProxy(instance)
    objc_mod._NSObjectBase = _NSObjectBase
    sys.modules["objc"] = objc_mod

    # ── mock NSRunningApplication ──────────────────────────────
    class _MockRunningApp:
        def __init__(self, name="TestApp"):
            self._name = name
            self.terminated = False
        def localizedName(self):
            return self._name
        def terminate(self):
            self.terminated = True
        def isTerminated(self):
            return self.terminated
        def activateWithOptions_(self, options):
            pass
        def bundleIdentifier(self):
            return "com.test.app"

    # ── mock NSWorkspace ──────────────────────────────────────
    _frontmost_app = _MockRunningApp("TestApp")

    class _MockWorkspace:
        @staticmethod
        def sharedWorkspace():
            return _MockWorkspace()
        def frontmostApplication(self):
            return _frontmost_app

    # ── Foundation ────────────────────────────────────────────
    foundation = types.ModuleType("Foundation")

    class _NSObject(_NSObjectBase):
        pass

    class _NSTimer:
        @staticmethod
        def scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            interval, target, selector, userinfo, repeats
        ):
            return MagicMock()
        def invalidate(self):
            pass

    class _NSDictionary:
        @staticmethod
        def dictionaryWithObject_forKey_(obj, key):
            return {key: obj}

    foundation.NSObject = _NSObject
    foundation.NSTimer = _NSTimer
    foundation.NSDictionary = _NSDictionary
    sys.modules["Foundation"] = foundation

    # ── AppKit ────────────────────────────────────────────────
    appkit = types.ModuleType("AppKit")
    appkit.NSFloatingWindowLevel = 8
    appkit.NSWorkspace = _MockWorkspace
    appkit._MockRunningApp = _MockRunningApp
    appkit._frontmost_app = _frontmost_app
    sys.modules["AppKit"] = appkit

    # ── Cocoa ─────────────────────────────────────────────────
    cocoa = types.ModuleType("Cocoa")
    cocoa.NSObject = _NSObject
    cocoa.NSApp = MagicMock()
    cocoa.NSApplication = MagicMock()
    cocoa.NSApplicationActivationPolicyAccessory = 1
    cocoa.NSAlertFirstButtonReturn = 1000

    # NSAlert mock
    _alert_instance = MagicMock()
    _alert_instance.runModal.return_value = 1000
    _alert_instance.window.return_value = MagicMock()
    _NSAlert = MagicMock(return_value=_alert_instance)
    _NSAlert.alloc.return_value = MagicMock(init=MagicMock(return_value=_alert_instance))
    cocoa.NSAlert = _NSAlert
    cocoa._alert_instance = _alert_instance

    cocoa.NSMenu = MagicMock()
    cocoa.NSMenuItem = MagicMock()
    cocoa.NSStatusBar = MagicMock()
    cocoa.NSVariableStatusItemLength = -1
    cocoa.NSFloatingWindowLevel = 8

    # settings_window.py 从 Cocoa 导入的 UI 组件
    cocoa.NSPanel = MagicMock()
    cocoa.NSButton = MagicMock()
    cocoa.NSTextField = MagicMock()
    cocoa.NSColor = MagicMock()
    cocoa.NSFont = MagicMock()
    cocoa.NSMakeRect = MagicMock(return_value=(0, 0, 0, 0))
    cocoa.NSWindowStyleMaskTitled = 1
    cocoa.NSWindowStyleMaskClosable = 2
    cocoa.NSWindowStyleMaskNonactivatingPanel = 128
    cocoa.NSBackingStoreBuffered = 2
    cocoa.NSTextAlignmentCenter = 1
    cocoa.NSTextAlignmentLeft = 0
    cocoa.NSWindowStyleMaskBorderless = 0
    sys.modules["Cocoa"] = cocoa

    # ── ApplicationServices ───────────────────────────────────
    appsvc = types.ModuleType("ApplicationServices")
    appsvc.AXIsProcessTrustedWithOptions = MagicMock(return_value=True)
    sys.modules["ApplicationServices"] = appsvc
