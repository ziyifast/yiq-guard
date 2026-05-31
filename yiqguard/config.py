import json
import os
import tempfile

CONFIG_DIR = os.path.expanduser("~/.yiq-guard")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "enabled": True,
    "mode": "double_press",  # "confirm" or "double_press"
    "settings_hotkey": {
        "ctrl": True,
        "option": True,
        "shift": False,
        "key": "q",
    },
    "quit_hotkey": {
        "ctrl": True,
        "option": True,
        "shift": True,
        "key": "q",
    },
}


def hotkey_to_str(hotkey):
    """将快捷键配置转换为可读字符串，如 'Ctrl+Option+Q'。"""
    parts = []
    if hotkey.get("ctrl"):
        parts.append("Ctrl")
    if hotkey.get("option"):
        parts.append("Option")
    if hotkey.get("shift"):
        parts.append("Shift")
    if hotkey.get("cmd"):
        parts.append("Cmd")
    parts.append(hotkey.get("key", "q").upper())
    return "+".join(parts)


def load():
    if not os.path.exists(CONFIG_FILE):
        return dict(DEFAULTS)
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        # 填补缺失字段
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"[Config] 加载配置失败，使用默认值: {e}")
        return dict(DEFAULTS)


def save(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=CONFIG_DIR)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=2)
        os.replace(tmp_path, CONFIG_FILE)
    except OSError as e:
        print(f"[Config] 保存配置失败: {e}")
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
