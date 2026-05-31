from ApplicationServices import AXIsProcessTrustedWithOptions
from Foundation import NSDictionary

_PROMPT_KEY = "AXTrustedCheckOptionPrompt"


def is_trusted(prompt=False):
    """
    检查当前进程是否拥有辅助功能权限。
    prompt=True 时若未授权会自动弹出系统授权引导弹窗。
    """
    if prompt:
        options = NSDictionary.dictionaryWithObject_forKey_(True, _PROMPT_KEY)
    else:
        options = None
    return AXIsProcessTrustedWithOptions(options)
