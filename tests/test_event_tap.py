"""
测试 event_tap.py：模块导入、队列结构、stop 不崩溃、超时常量、快捷键配置
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mocks.macos_mocks import install_mocks
install_mocks()

from yiqguard.event_tap import (
    EventTap,
    _CMD_Q_KEYCODE,
    _CMD_FLAG,
    _ALT_FLAG,
    _SHIFT_FLAG,
    _CTRL_FLAG,
    _TAP_DISABLED_BY_TIMEOUT,
    _TAP_DISABLED_BY_USER_INPUT,
    _EVENT_MASK,
    _KEYCODE_MAP,
    _build_hotkey_flags,
)
import queue


def test_event_tap_init():
    tap = EventTap()
    assert tap.event_queue is not None
    assert isinstance(tap.event_queue, queue.Queue)
    assert tap._tap is None
    assert tap._thread is None


def test_event_tap_init_default_hotkey():
    """默认快捷键应为 Ctrl+Option+Q。"""
    tap = EventTap()
    expected_flags = _CTRL_FLAG | _ALT_FLAG
    assert tap._hotkey_flags == expected_flags
    assert tap._hotkey_keycode == 12  # Q


def test_event_tap_init_custom_hotkey():
    """支持自定义快捷键配置。"""
    config = {"ctrl": True, "option": False, "shift": True, "key": "s"}
    tap = EventTap(hotkey_config=config)
    expected_flags = _CTRL_FLAG | _SHIFT_FLAG
    assert tap._hotkey_flags == expected_flags
    assert tap._hotkey_keycode == _KEYCODE_MAP["s"]


def test_event_tap_stop_when_not_started():
    tap = EventTap()
    tap.stop()  # 不应抛出异常


def test_event_queue_is_thread_safe():
    tap = EventTap()
    tap.event_queue.put("cmd_q")
    msg = tap.event_queue.get_nowait()
    assert msg == "cmd_q"


def test_event_queue_open_settings():
    tap = EventTap()
    tap.event_queue.put("open_settings")
    msg = tap.event_queue.get_nowait()
    assert msg == "open_settings"


def test_cmd_q_keycode():
    assert _CMD_Q_KEYCODE == 12


def test_build_hotkey_flags_default():
    """Ctrl+Option+Q 的 flags 构建正确。"""
    config = {"ctrl": True, "option": True, "shift": False, "key": "q"}
    flags, keycode = _build_hotkey_flags(config)
    assert flags == (_CTRL_FLAG | _ALT_FLAG)
    assert keycode == 12


def test_build_hotkey_flags_all_modifiers():
    """全部修饰键组合构建正确。"""
    config = {"ctrl": True, "option": True, "shift": True, "cmd": True, "key": "a"}
    flags, keycode = _build_hotkey_flags(config)
    assert flags == (_CTRL_FLAG | _ALT_FLAG | _SHIFT_FLAG | _CMD_FLAG)
    assert keycode == 0  # A


def test_keycode_map_has_all_letters():
    """keycode 映射表应包含 a-z 全部 26 个字母。"""
    for c in "abcdefghijklmnopqrstuvwxyz":
        assert c in _KEYCODE_MAP


def test_tap_disabled_constants_not_in_mask():
    """超时常量不能用于 CGEventMaskBit，确认未加入 event mask。"""
    import Quartz
    key_down_bit = Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
    assert _EVENT_MASK == key_down_bit


def test_tap_disabled_values_are_large():
    """超时常量值超过普通 uint32 范围，不适合 CGEventMaskBit。"""
    assert _TAP_DISABLED_BY_TIMEOUT > 0xFFFF0000
    assert _TAP_DISABLED_BY_USER_INPUT > 0xFFFF0000
