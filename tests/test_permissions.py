"""
测试 permissions.py：is_trusted 参数传递
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mocks.macos_mocks import install_mocks
install_mocks()

import yiqguard.permissions as permissions
from unittest.mock import patch


def test_is_trusted_no_prompt_passes_none():
    with patch("yiqguard.permissions.AXIsProcessTrustedWithOptions", return_value=True) as mock_ax:
        result = permissions.is_trusted(prompt=False)
        assert result is True
        mock_ax.assert_called_once_with(None)


def test_is_trusted_with_prompt_passes_dict():
    with patch("yiqguard.permissions.AXIsProcessTrustedWithOptions", return_value=False) as mock_ax:
        result = permissions.is_trusted(prompt=True)
        assert result is False
        args = mock_ax.call_args[0][0]
        # 应该传入包含 prompt key 的 dict
        assert args is not None
        assert "AXTrustedCheckOptionPrompt" in args
        assert args["AXTrustedCheckOptionPrompt"] is True
