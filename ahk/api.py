from contextlib import contextmanager
from functools import partial

import _ahk  # noqa


__all__ = [
    "Error", "Timer",
    "message_box", "hotkey", "remap_key", "hotkey_context", "send", "send_mode",
    "set_batch_lines", "detect_hidden_windows", "set_title_match_mode",
    "win_exist", "set_timer", "get_key_state",
]

Error = _ahk.Error


def message_box(text=None, title="", options=0, timeout=None):
    if text is None:
        # Show "Press OK to continue."
        return _ahk.call("MsgBox")

    return _ahk.call("MsgBox", options, title, str(text), timeout)
    # TODO: Return result of IfMsgBox?


def hotkey(key_name, func=None, buffer=None, priority=0, max_threads=None,
           input_level=None):
    if key_name == "":
        raise Error("invalid key name")

    if func is None:
        # Return the decorator.
        return partial(hotkey, key_name, buffer=buffer, priority=priority,
                       max_threads=max_threads, input_level=input_level)

    # TODO: Handle case when func == "AltTab" or other substitutes.
    # TODO: Set the options.
    # TODO: Change options of the existing hotkeys.
    # TODO: Return a Hotkey object.
    _ahk.call("Hotkey", key_name, func)


def remap_key(origin_key, destination_key):
    # TODO: Implement key remapping, e.g. Esc::CapsLock.
    raise NotImplementedError()


@contextmanager
def hotkey_context():
    # TODO: Implement `Hotkey, If` commands.
    raise NotImplementedError()


def send(keys):
    # TODO: Consider adding `mode` keyword?
    _ahk.call("Send", keys)


def send_mode(mode):
    _ahk.call("SendMode", mode)


def set_batch_lines(interval=None, lines=None):
    if interval is not None:
        _ahk.call("SetBatchLines", f"{interval}ms")
        return
    if lines is not None:
        _ahk.call("SetBatchLines", f"{lines}")
        return
    raise ValueError("either 'interval' or 'lines' are required")


def detect_hidden_windows(value):
    value = "On" if value else "Off"
    _ahk.call("DetectHiddenWindows", value)


def set_title_match_mode(mode=None, speed=None):
    if mode is not None:
        match_modes = {
            "startswith": "1",
            "contains": "2",
            "exact": "3",
            "1": "1",
            "2": "2",
            "3": "3",
            "regex": "regex",
        }
        ahk_mode = match_modes.get(str(mode).lower())
        if ahk_mode is None:
            raise ValueError(f"unknown match mode {mode!r}")
        _ahk.call("SetTitleMatchMode", ahk_mode)

    if speed is not None:
        speeds = ["fast", "slow"]
        if speed.lower() not in speeds:
            raise ValueError(f"unknown speed {speed!r}")
        _ahk.call("SetTitleMatchMode", speed)


def win_exist(win_title, win_text="", exclude_title="", exclude_text=""):
    # TODO: Check that empty strings work in this case.
    return _ahk.call(win_title, win_text, exclude_title, exclude_text)


def set_timer(func=None, period=0.25, countdown=None, priority=0):
    if func is None:
        # Return the decorator.
        return partial(set_timer, period=period, countdown=countdown, priority=priority)

    if countdown is not None:
        if countdown < 0:
            raise ValueError("countdown must be positive")
        period = -countdown
    period = int(period*1000)

    _ahk.call("SetTimer", func, period, priority)

    return Timer(func)


class Timer:
    def __init__(self, func):
        self._func = func

    def enable(self):
        _ahk.call("SetTimer", self._func, "On")

    def disable(self):
        _ahk.call("SetTimer", self._func, "Off")

    def delete(self):
        _ahk.call("SetTimer", self._func, "Delete")

    def set_priority(self, priority):
        _ahk.call("SetTimer", self._func, "", priority)


def get_key_state(key_name, mode=None):
    return _ahk.call("GetKeyState", key_name, mode)
