import _ahk  # noqa

__all__ = [
    "get_clipboard",
    "set_clipboard",
    "wait_clipboard",
]


def get_clipboard():
    return _ahk.call("GetClipboard")


def set_clipboard(value):
    return _ahk.call("SetClipboard", str(value))


def wait_clipboard(timeout=None):
    # TODO: Implement WaitForAnyData argument.
    if timeout is not None:
        timeout = float(timeout)
    timed_out = _ahk.call("ClipWait", timeout)
    if timed_out:
        return ""
    return get_clipboard()


# TODO: Implement ClipboardAll.
