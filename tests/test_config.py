"""
测试 config.py：配置读写、默认值、原子写入
"""
import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mocks.macos_mocks import install_mocks
install_mocks()

import yiqguard.config as config


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    """每个测试用独立的临时目录。"""
    monkeypatch.setattr(config, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(config, "CONFIG_FILE", str(tmp_path / "config.json"))


def test_load_returns_defaults_when_no_file():
    cfg = config.load()
    assert cfg["enabled"] is True
    assert cfg["mode"] == "double_press"


def test_save_and_load_roundtrip():
    cfg = {"enabled": False, "mode": "double_press"}
    config.save(cfg)
    loaded = config.load()
    assert loaded["enabled"] is False
    assert loaded["mode"] == "double_press"


def test_load_fills_missing_keys():
    # 只写一个字段，另一个应该用默认值填补
    config.save({"enabled": False, "mode": "confirm"})
    # 手动删掉一个字段
    with open(config.CONFIG_FILE, "w") as f:
        json.dump({"enabled": False}, f)
    loaded = config.load()
    assert loaded["enabled"] is False
    assert loaded["mode"] == "double_press"  # 默认值填补


def test_load_returns_defaults_on_corrupt_file():
    os.makedirs(config.CONFIG_DIR, exist_ok=True)
    with open(config.CONFIG_FILE, "w") as f:
        f.write("not valid json {{{")
    cfg = config.load()
    assert cfg == dict(config.DEFAULTS)


def test_save_creates_dir_if_missing(tmp_path, monkeypatch):
    new_dir = str(tmp_path / "nested" / "config")
    monkeypatch.setattr(config, "CONFIG_DIR", new_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", os.path.join(new_dir, "config.json"))
    config.save({"enabled": True, "mode": "confirm"})
    assert os.path.exists(os.path.join(new_dir, "config.json"))


def test_defaults_include_settings_hotkey():
    """默认配置应包含 settings_hotkey 字段。"""
    cfg = config.load()
    assert "settings_hotkey" in cfg
    hotkey = cfg["settings_hotkey"]
    assert hotkey["ctrl"] is True
    assert hotkey["option"] is True
    assert hotkey["shift"] is False
    assert hotkey["key"] == "q"
