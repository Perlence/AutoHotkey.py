from typing import NamedTuple
from functools import partial

import _ahk  # noqa

__all__ = [
    "Timer", "set_batch_lines", "set_timer",
]


def set_batch_lines(interval=None, lines=None):
    if interval is not None:
        _ahk.call("SetBatchLines", f"{interval}ms")
        return
    if lines is not None:
        _ahk.call("SetBatchLines", f"{lines}")
        return
    raise ValueError("either 'interval' or 'lines' are required")


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


class Timer(NamedTuple):
    func: callable

    def enable(self):
        _ahk.call("SetTimer", self.func, "On")

    def disable(self):
        _ahk.call("SetTimer", self.func, "Off")

    def delete(self):
        # TODO: Remove self.func from CALLBACKS and BOUND_TRIGGERS.
        _ahk.call("SetTimer", self.func, "Delete")

    def set_priority(self, priority):
        _ahk.call("SetTimer", self.func, "", priority)
