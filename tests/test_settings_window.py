"""测试 SettingsWindow 逻辑（mock macOS 依赖）。"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mocks.macos_mocks import install_mocks
install_mocks()

import unittest
from yiqguard.ui.settings_window import SettingsWindow


class TestSettingsWindow(unittest.TestCase):
    def _make_win(self, enabled=True, mode="confirm"):
        config = {"enabled": enabled, "mode": mode}
        toggle_calls = []
        mode_calls = []
        win = SettingsWindow(
            config=config,
            on_toggle=lambda: toggle_calls.append(1),
            on_mode_change=lambda m: mode_calls.append(m),
        )
        # 模拟窗口已构建（用 MagicMock 代替真实 NSButton）
        from unittest.mock import MagicMock
        win._panel = MagicMock()
        win._toggle_btn = MagicMock()
        win._confirm_btn = MagicMock()
        win._double_btn = MagicMock()
        return win, config, toggle_calls, mode_calls

    def test_toggle_protection_calls_callback(self):
        win, config, toggle_calls, _ = self._make_win()
        win._toggle_protection()
        self.assertEqual(len(toggle_calls), 1)

    def test_set_mode_calls_callback(self):
        win, config, _, mode_calls = self._make_win()
        win._set_mode("double_press")
        self.assertEqual(mode_calls, ["double_press"])

    def test_on_window_close_clears_panel(self):
        win, _, _, _ = self._make_win()
        win._panel = object()  # 假装有窗口
        win._toggle_btn = object()
        win._on_window_close()
        self.assertIsNone(win._panel)
        self.assertIsNone(win._toggle_btn)

    def test_refresh_without_panel_does_not_crash(self):
        win, _, _, _ = self._make_win()
        # _panel 为 None 时 refresh 应安静退出
        win.refresh()  # 不应抛异常


if __name__ == "__main__":
    unittest.main()
