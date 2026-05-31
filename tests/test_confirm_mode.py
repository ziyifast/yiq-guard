"""
测试 confirm_mode.py：弹窗确认逻辑
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mocks.macos_mocks import install_mocks
install_mocks()


def test_confirm_quit_calls_on_quit_with_app():
    """用户点退出时，on_quit 应收到 frontmost_app。"""
    from AppKit import _frontmost_app
    import yiqguard.modes.confirm_mode as cm

    received = []

    # NSAlert mock 已在 macos_mocks 中配置为返回 NSAlertFirstButtonReturn（退出）
    cm.handle(on_quit=lambda app: received.append(app))

    assert len(received) == 1
    assert received[0] is _frontmost_app


def test_confirm_cancel_does_not_call_on_quit():
    """用户点取消时，on_quit 不应被调用。"""
    import sys
    import Cocoa
    import yiqguard.modes.confirm_mode as cm

    # 让 runModal 返回取消（第二个按钮 = 1001）
    Cocoa._alert_instance.runModal.return_value = 1001

    received = []
    cm.handle(on_quit=lambda app: received.append(app))
    assert received == []

    # 恢复
    Cocoa._alert_instance.runModal.return_value = 1000


def test_confirm_shows_app_name_in_message():
    """弹窗信息文本中应包含前台应用名称。"""
    import Cocoa
    import yiqguard.modes.confirm_mode as cm

    Cocoa._alert_instance.runModal.return_value = 1001  # 取消，不退出
    cm.handle(on_quit=lambda app: None)

    # 验证 setInformativeText_ 被调用且包含应用名
    call_args = Cocoa._alert_instance.setInformativeText_.call_args
    assert call_args is not None
    text = call_args[0][0]
    assert "TestApp" in text

    # 恢复
    Cocoa._alert_instance.runModal.return_value = 1000
