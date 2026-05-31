"""
弹窗确认模式：
- 弹出置顶确认对话框
- 用户点「退出」时，通过 NSRunningApplication 直接终止前台应用
- 用户点「取消」时，将焦点还给原来的应用
- 必须在主线程调用
"""
from AppKit import (
    NSFloatingWindowLevel,
    NSWorkspace,
)
from Cocoa import (
    NSAlert,
    NSAlertFirstButtonReturn,
    NSApp,
)


def handle(on_quit):
    """
    弹出置顶确认对话框。
    用户点「退出」时调用 on_quit(app)，点「取消」则恢复焦点到原应用。
    必须在主线程调用，调用前需先记录当前前台应用。
    """
    # 在弹窗出现前先记录当前前台应用（弹窗会抢走焦点）
    workspace = NSWorkspace.sharedWorkspace()
    frontmost_app = workspace.frontmostApplication()

    alert = NSAlert.alloc().init()
    alert.setMessageText_("确认退出？")
    alert.setInformativeText_(
        f"你按下了 Command+Q。确定要退出「{frontmost_app.localizedName()}」吗？"
    )
    alert.addButtonWithTitle_("退出")
    alert.addButtonWithTitle_("取消")

    # 置于所有窗口最前面
    alert.window().setLevel_(NSFloatingWindowLevel)
    NSApp.activateIgnoringOtherApps_(True)

    result = alert.runModal()
    if result == NSAlertFirstButtonReturn:
        on_quit(frontmost_app)
    else:
        # 取消时将焦点还给原来的应用
        _reactivate_app(frontmost_app)


def _reactivate_app(app):
    """将焦点还给指定应用。"""
    if app and not app.isTerminated():
        app.activateWithOptions_(0)
