import ctypes
import dataclasses as dc
import queue
import sys
import threading
from typing import Callable

import _ahk

__all__ = [
    "Timer",
    "coop",
    "output_debug",
    "reload",
    "resume",
    "set_timer",
    "sleep",
    "suspend",
    "toggle_suspend",
]


global_ahk_lock = threading.RLock()


def ahk_call(cmd, *args):
    # AHK callbacks are not reentrant. While the main thread is busy executing
    # an AHK function, trying to call another AHK function from another thread
    # leads to unpredictable results like program crash. The following lock
    # allows only one system thread to call AHK.
    with global_ahk_lock:
        return _ahk.call(cmd, *args)


def set_timer(func=None, period=0.25, countdown=None, priority=0):
    # TODO: Separate one-time and periodic timers into two different functions.
    if countdown is not None:
        if countdown < 0:
            raise ValueError("countdown must be positive")
        period = -countdown
    period = int(period*1000)

    def set_timer_decorator(func):
        ahk_call("SetTimer", func, period, priority)
        return Timer(func)

    if func is None:
        return set_timer_decorator
    return set_timer_decorator(func)


@dc.dataclass(frozen=True)
class Timer:
    func: Callable
    __slots__ = ("func",)

    def start(self):
        # FIXME: start() resets a finished one-time timer and makes it periodic
        # with the default 0.25 second period. This happens because AHK recycles
        # the function reference after the countdown, so it's no longer in
        # WRAPPED_PYTHON_FUNCTIONS.
        ahk_call("SetTimer", self.func, "On")

    def stop(self):
        ahk_call("SetTimer", self.func, "Off")

    def cancel(self):
        ahk_call("SetTimer", self.func, "Delete")

    def set_priority(self, priority):
        ahk_call("SetTimer", self.func, "", priority)

    def update(self, period=None, countdown=None, priority=None):
        if period is None and countdown is None and priority is None:
            return
        if countdown is not None:
            if countdown < 0:
                raise ValueError("countdown must be positive")
            period = -countdown
        period = int(period*1000) if period is not None else ""
        priority = priority if priority is not None else ""
        ahk_call("SetTimer", self.func, period, priority)


def sleep(secs):
    if secs < 0:
        raise ValueError("sleep length must be non-negative")
    elif secs == 0:
        # XXX: Should it be -1 or 0?
        ahk_call("Sleep", -1)
    else:
        ahk_call("Sleep", int(secs * 1000))


def suspend():
    ahk_call("Suspend", "On")


def resume():
    ahk_call("Suspend", "Off")


def toggle_suspend():
    ahk_call("Suspend", "Toggle")


def reload():
    # TODO: If the new script has an error, AHK will show it and quit. Instead,
    # keep the old script running.
    from . import launcher
    sys.exit(launcher.EXIT_CODE_RELOAD)


def output_debug(*objs, sep=" "):
    if sep is None:
        # Python documentation for the print() function:
        #
        # > Both *sep* and *end* must be strings; they can also be `None`, which
        # > means to use the default values.
        sep = " "
    debug_str = sep.join(map(str, objs))
    ctypes.windll.kernel32.OutputDebugStringW(debug_str)


def coop(func, *args, **kwargs):
    """Run the given function in a new thread and make it cooperate with AHK's
    event loop.

    Use *coop* to execute **pre-existing** long-running I/O bound Python
    processes like HTTP servers and stdin readers that are designed to handle
    KeyboardInterrupt:

    .. code-block:: python

        import code
        import ahkpy as ahk
        ahk.coop(code.interact)

    The call starts a new thread and blocks the current thread until the
    function finishes. Returns the result of the function or raises the
    exception.

    Whenever KeyboardInterrupt occurs in the current thread, it's propagated to
    the background thread so it could stop.

    If you start your own threads, be sure to yield the control back to AHK so
    it could process its message queue:

    .. code-block:: python

        import threading
        th = threading.Thread(target=some_worker)
        th.start()
        while th.is_alive():
            # Important: Let AHK handle its message queue.
            ahk.sleep(0.01)
    """
    q = queue.Queue(maxsize=1)
    th = threading.Thread(
        target=_run_coop,
        args=(q, func, args, kwargs),
        daemon=True,
    )
    th.start()
    while True:
        try:
            if not th.is_alive():
                break
            sleep(0.01)
        except KeyboardInterrupt:
            set_async_exc = ctypes.pythonapi.PyThreadState_SetAsyncExc
            thread_id = th.ident
            kbd_interrupt = ctypes.py_object(KeyboardInterrupt)
            if th.is_alive():
                set_async_exc(thread_id, kbd_interrupt)

    try:
        val, exc = q.get_nowait()
    except queue.Empty:
        raise RuntimeError("coop thread did not return a value") from None
    if exc is not None:
        raise exc
    return val


def _run_coop(queue, func, args, kwargs):
    try:
        result = func(*args, **kwargs), None
    except BaseException as exc:
        # Catch BaseException because we also want SystemExit and
        # KeyboardInterrupt.
        result = None, exc
    queue.put(result)
