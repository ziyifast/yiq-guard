"""
测试 double_press_mode.py：单击不触发、双击触发、超时重置、on_first_press 回调
"""
import os
import sys
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mocks.macos_mocks import install_mocks
install_mocks()

from yiqguard.modes.double_press_mode import DoublePressMode, DOUBLE_PRESS_INTERVAL


def test_single_press_does_not_quit():
    mode = DoublePressMode()
    quit_called = []
    mode.handle(on_quit=lambda app: quit_called.append(app))
    assert quit_called == []


def test_double_press_within_interval_quits():
    mode = DoublePressMode()
    quit_called = []
    mode.handle(on_quit=lambda app: quit_called.append(app))
    mode.handle(on_quit=lambda app: quit_called.append(app))
    assert len(quit_called) == 1


def test_double_press_after_timeout_does_not_quit():
    mode = DoublePressMode()
    quit_called = []
    mode.handle(on_quit=lambda app: quit_called.append(app))
    mode._last_press_time -= (DOUBLE_PRESS_INTERVAL + 0.1)
    mode.handle(on_quit=lambda app: quit_called.append(app))
    assert quit_called == []


def test_reset_clears_state():
    mode = DoublePressMode()
    mode._last_press_time = time.time()
    mode._target_app = object()
    mode.reset()
    assert mode._last_press_time == 0.0
    assert mode._target_app is None


def test_after_quit_state_is_reset():
    mode = DoublePressMode()
    quit_called = []
    mode.handle(on_quit=lambda app: quit_called.append(app))
    mode.handle(on_quit=lambda app: quit_called.append(app))
    assert len(quit_called) == 1
    # 再次单击不应触发
    mode.handle(on_quit=lambda app: quit_called.append(app))
    assert len(quit_called) == 1


def test_on_quit_receives_first_press_app():
    """第二次按下时，on_quit 收到的是第一次按下时记录的 app，不是当时的 frontmost。"""
    mode = DoublePressMode()
    received = []
    mode.handle(on_quit=lambda app: None)                      # 第一次，记录 app
    recorded_app = mode._target_app                            # 拿到记录的 app
    mode.handle(on_quit=lambda app: received.append(app))      # 第二次触发
    assert len(received) == 1
    assert received[0] is recorded_app  # 必须是第一次记录的，不是重新获取的


def test_first_press_calls_on_first_press():
    """第一次按下时 on_first_press 应被调用，传入应用名。"""
    mode = DoublePressMode()
    first_press_names = []
    mode.handle(
        on_quit=lambda app: None,
        on_first_press=lambda name: first_press_names.append(name),
    )
    assert len(first_press_names) == 1
    assert isinstance(first_press_names[0], str)


def test_second_press_does_not_call_on_first_press():
    """第二次按下（触发退出）时 on_first_press 不应被调用。"""
    mode = DoublePressMode()
    first_press_names = []
    quit_called = []
    mode.handle(
        on_quit=lambda app: quit_called.append(app),
        on_first_press=lambda name: first_press_names.append(name),
    )
    mode.handle(
        on_quit=lambda app: quit_called.append(app),
        on_first_press=lambda name: first_press_names.append(name),
    )
    assert len(quit_called) == 1
    assert len(first_press_names) == 1  # 只在第一次调用


def test_on_first_press_none_is_safe():
    """不传 on_first_press 时不应报错。"""
    mode = DoublePressMode()
    mode.handle(on_quit=lambda app: None)  # 不传 on_first_press
