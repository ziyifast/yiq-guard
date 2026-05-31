"""
测试模块导入：确保所有模块都能正确导入，无循环依赖、无拼写错误
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mocks.macos_mocks import install_mocks
install_mocks()


def test_import_config():
    import yiqguard.config


def test_import_permissions():
    import yiqguard.permissions


def test_import_event_tap():
    import yiqguard.event_tap


def test_import_confirm_mode():
    import yiqguard.modes.confirm_mode


def test_import_double_press_mode():
    import yiqguard.modes.double_press_mode


def test_import_menu_bar():
    import yiqguard.ui.menu_bar


def test_import_settings_window():
    import yiqguard.ui.settings_window


def test_import_toast():
    import yiqguard.ui.toast


def test_import_app_delegate():
    import yiqguard.app_delegate


def test_import_main():
    import main
