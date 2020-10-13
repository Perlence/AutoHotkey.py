import ctypes
import dataclasses as dc
import functools
import queue
import sys
import threading
import weakref
from typing import Callable, Optional

import _ahk

__all__ = [
    "Countdown",
    "Timer",
    "coop",
    "output_debug",
    "reload",
    "resume",
    "set_countdown",
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


def set_timer(func=None, interval=0.25, priority=0):
    t = Timer(func, interval, priority)

    def set_timer_decorator(func):
        t.func = func
        t.start()
        return t

    if func is None:
        return set_timer_decorator
    return set_timer_decorator(func)


def set_countdown(func=None, interval=0.25, priority=0):
    t = Countdown(func, interval, priority)

    def set_countdown_decorator(func):
        t.func = func
        t.start()
        return t

    if func is None:
        return set_countdown_decorator
    return set_countdown_decorator(func)


@dc.dataclass(eq=False)
class Timer:
    func: Callable
    interval: float = 0.25
    priority: int = 0

    def __init__(self, func, interval=0.25, priority=0):
        self.func = func

        if interval < 0:
            raise ValueError("interval must be positive")
        self.interval = interval

        if not -2147483648 <= priority <= 2147483647:
            raise ValueError("priority must be between -2147483648 and 2147483647")
        self.priority = priority

        self._ref: Optional[weakref.ReferenceType] = None

    def start(self, interval=None, priority=None):
        force_restart = interval is None
        self.update(interval=interval, priority=priority, force_restart=force_restart)

    def update(self, func=None, interval=None, priority=None, force_restart=False):
        if func is not None:
            self.cancel()
            self.func = func
            self._ref = None

        # When AHK timer is deleted it releases the reference to the passed
        # callback. We can use this to check if the timer is alive.
        func_wrapper = None
        if self._ref is not None:
            func_wrapper = self._ref()
        if func_wrapper is None:
            # AHK timer was deleted or never started.
            if not callable(self.func):
                raise TypeError("timer callback must be callable")
            func_wrapper = functools.partial(self.func)
            self._ref = weakref.ref(func_wrapper)
            force_restart = True

        if interval is None and priority is None and not force_restart:
            return

        if interval is not None or force_restart:
            if interval is None:
                interval = self.interval
            if interval < 0:
                raise ValueError("interval must be positive")
            self.interval = interval
            interval = int(interval * 1000)
        else:
            interval = ""

        if priority is not None or force_restart:
            if priority is None:
                priority = self.priority
            if not -2147483648 <= priority <= 2147483647:
                raise ValueError("priority must be between -2147483648 and 2147483647")
            self.priority = priority
        else:
            priority = ""

        self._update(func_wrapper, interval, priority)

    def _update(self, func, interval, priority):
        ahk_call("SetTimer", func, interval, priority)

    def stop(self):
        if not self._ref:
            return
        func = self._ref()
        if func is not None:
            ahk_call("SetTimer", func, "Delete")


class Countdown(Timer):
    def _update(self, func, interval, priority):
        ahk_call("SetTimer", func, -interval, priority)


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
