import _ahk

__all__ = [
    "get_clipboard",
    "set_clipboard",
]


def get_clipboard():
    return _ahk.call("GetClipboard")


def set_clipboard(value):
    return _ahk.call("SetClipboard", str(value))
