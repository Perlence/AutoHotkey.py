from dataclasses import dataclass
from functools import partial
from typing import Callable

import _ahk  # noqa

__all__ = [
    "Timer",
    "resume",
    "set_timer",
    "sleep",
    "suspend",
    "toggle_suspend",
]


def set_timer(func=None, period=0.25, countdown=None, priority=0):
    # TODO: Should this be threading.Timer?
    if func is None:
        # Return the decorator.
        return partial(set_timer, period=period, countdown=countdown, priority=priority)

    if countdown is not None:
        if countdown < 0:
            raise ValueError("countdown must be positive")
        period = -countdown
    period = int(period*1000)

    _ahk.call("SetTimer", func, period, priority)

    # TODO: Remove func from CALLBACKS after its execution if *countdown* is set.
    return Timer(func)


@dataclass(frozen=True)
class Timer:
    func: Callable

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
