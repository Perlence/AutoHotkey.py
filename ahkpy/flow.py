import os
import sys
from ctypes import windll
from dataclasses import dataclass
from typing import Callable

import _ahk  # noqa

__all__ = [
    "Timer",
    "output_debug",
    "reload",
    "resume",
    "set_timer",
    "sleep",
    "suspend",
    "toggle_suspend",
]


def set_timer(func=None, period=0.25, countdown=None, priority=0):
    # XXX: Should this be threading.Timer?
    if countdown is not None:
        if countdown < 0:
            raise ValueError("countdown must be positive")
        period = -countdown
    period = int(period*1000)

    def set_timer_decorator(func):
        _ahk.call("SetTimer", func, period, priority)
        # TODO: Remove func from CALLBACKS after its execution if *countdown* is set.
        return Timer(func)

    if func is None:
        return set_timer_decorator
    return set_timer_decorator(func)


@dataclass(frozen=True)
class Timer:
    func: Callable
    __slots__ = tuple(__annotations__.keys())

    def start(self):
        _ahk.call("SetTimer", self.func, "On")

    def stop(self):
        _ahk.call("SetTimer", self.func, "Off")

    def cancel(self):
        # TODO: Remove self.func from CALLBACKS and WRAPPED_PYTHON_FUNCTIONS in AHK.
        _ahk.call("SetTimer", self.func, "Delete")

    def set_priority(self, priority):
        _ahk.call("SetTimer", self.func, "", priority)


def sleep(secs):
    if secs < 0:
        raise ValueError("sleep length must be non-negative")
    elif secs == 0:
        _ahk.call("Sleep", -1)
    else:
        _ahk.call("Sleep", int(secs * 1000))


def suspend():
    _ahk.call("Suspend", "On")


def resume():
    _ahk.call("Suspend", "Off")


def toggle_suspend():
    _ahk.call("Suspend", "Toggle")


def reload():
    # TODO: If the new script has an error, AHK will show it and quit. Instead,
    # keep the old script running.
    _ahk.call("Menu", "Tray", "NoIcon")
    args = list(map(_quote, [sys.executable, _ahk.script_full_path] + sys.argv))
    os.execv(sys.executable, args)


def _quote(s):
    return f'"{s}"'


def output_debug(*objs, sep=' '):
    if sep is None:
        # Python documentation for the print() function:
        #
        # > Both *sep* and *end* must be strings; they can also be `None`, which
        # > means to use the default values.
        sep = ' '
    debug_str = sep.join(map(str, objs))
    windll.kernel32.OutputDebugStringW(debug_str)
