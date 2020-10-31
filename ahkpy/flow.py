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


def ahk_call(cmd: str, *args):
    """Call the arbitrary AHK command/function *cmd* with *args* arguments.

    Use this function only when there's no appropriate API provided by
    AutoHotkey.py.
    """
    # AHK callbacks are not reentrant. While the main thread is busy executing
    # an AHK function, trying to call another AHK function from another thread
    # leads to unpredictable results like program crash. The following lock
    # allows only one system thread to call AHK.
    with global_ahk_lock:
        return _ahk.call(cmd, *args)


def set_timer(interval=0.25, func=None, *args, priority=0):
    """Create a timer that will run *func* periodically with arguments *args*
    after *interval* seconds have passed.

    If you want the function to be called with keyword arguments use
    :func:`functools.partial`.

    The optional parameter *priority* is an integer between -2147483648 and
    2147483647.

    AutoHotkey command: `SetTimer
    <https://www.autohotkey.com/docs/commands/SetTimer.htm>`_.
    """
    # TODO: Does priority actually work in ahkpy? It seems that other AHK
    # threads cannot interrupt the current AHK thread while it executes Python
    # code.
    t = Timer(interval, func, priority, periodic=True)

    def set_timer_decorator(func):
        if args:
            func = functools.partial(func, *args)
        t.func = func
        t.start()
        return t

    if func is None:
        return set_timer_decorator
    return set_timer_decorator(func)


def set_countdown(interval=0.25, func=None, *args, priority=0):
    """Create a timer that will run *func* once with arguments *args* after
    *interval* seconds have passed.

    If you want the function to be called with keyword arguments use
    :func:`functools.partial`.

    The optional parameter *priority* is an integer between -2147483648 and
    2147483647.

    AutoHotkey command: `SetTimer
    <https://www.autohotkey.com/docs/commands/SetTimer.htm>`_.
    """
    t = Timer(interval, func, priority, periodic=False)

    def set_countdown_decorator(func):
        if args:
            func = functools.partial(func, *args)
        t.func = func
        t.start()
        return t

    if func is None:
        return set_countdown_decorator
    return set_countdown_decorator(func)


@dc.dataclass(eq=False)
class Timer:
    """This class represents an action that should be run after a certain amount
    of time has passed.

    Creating an instance of :class:`!Timer` doesn't register the function in
    AHK. Use :func:`set_timer` or :func:`set_countdown` instead.
    """

    interval: float = 0.25
    func: Optional[Callable] = None
    priority: int = 0
    periodic: bool = True

    def __init__(self, interval=0.25, func=None, priority=0, periodic=True):
        self.func = func

        if interval < 0:
            raise ValueError("interval must be positive")
        self.interval = interval

        if not -2147483648 <= priority <= 2147483647:
            raise ValueError("priority must be between -2147483648 and 2147483647")
        self.priority = priority

        self.periodic = periodic

        self._ref: Optional[weakref.ReferenceType] = None

    def start(self, interval=None, priority=None, periodic=None):
        """Start a stopped timer or restart a running timer.

        If the *interval*, *priority*, or *periodic* arguments are passed, the
        :class:`!Timer` instance will be updated with the new values. See
        :meth:`Timer.update`.
        """
        self.update(interval=interval, priority=priority, force_restart=True)

    def update(self, func=None, interval=None, priority=None, periodic=None, force_restart=False):
        """Update the parameters of a timer and register them in AHK.

        Passing any of *func*, *interval*, or *periodic* arguments restarts the
        timer. Passing only the *priority* argument updates the timer without
        restarting.

        .. note::

            Changing the attributes of the timer instance doesn't affect the
            underlying AHK timer. Call the :meth:`Timer.update` to actually
            apply the changes to the AHK timer.

            .. code-block::

                t = ahkpy.set_timer(1, print, "beep")
                t.interval = 0.5
                # ^^ Does not change the frequency of prints!

                t.update()  # Makes the timer fire twice a second.
        """
        # TODO: Check that self.func is not None.
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

        if interval is not None or periodic is not None or force_restart:
            if interval is None:
                interval = self.interval
            if interval < 0:
                raise ValueError("interval must be positive")
            self.interval = interval
            interval = int(interval * 1000)

            if periodic is not None:
                self.periodic = bool(periodic)
            if not self.periodic:
                interval *= -1
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

        if interval != "" or priority != "":
            ahk_call("SetTimer", func_wrapper, interval, priority)

    def stop(self):
        """Stop the timer."""
        if not self._ref:
            return
        func = self._ref()
        if func is not None:
            ahk_call("SetTimer", func, "Delete")


def sleep(secs):
    """Suspend execution of the calling thread for the given number of seconds.

    During the wait, AHK checks its message queue and handles hotkeys and other
    callbacks.

    AutoHotkey command: `Sleep
    <https://www.autohotkey.com/docs/commands/Sleep.htm>`_.
    """
    if secs < 0:
        raise ValueError("sleep length must be non-negative")
    elif secs == 0:
        # TODO: Should it be -1 or 0?
        ahk_call("Sleep", -1)
    else:
        ahk_call("Sleep", int(secs * 1000))


def suspend():
    """Disable all hotkeys and hotstrings.

    AutoHotkey command: `Suspend
    <https://www.autohotkey.com/docs/commands/Suspend.htm>`_.
    """
    ahk_call("Suspend", "On")


def resume():
    """Enable all hotkeys and hotstrings.

    AutoHotkey command: `Suspend
    <https://www.autohotkey.com/docs/commands/Suspend.htm>`_.
    """
    ahk_call("Suspend", "Off")


def toggle_suspend():
    """Toggle all hotkeys and hotstrings.

    AutoHotkey command: `Suspend
    <https://www.autohotkey.com/docs/commands/Suspend.htm>`_.
    """
    ahk_call("Suspend", "Toggle")


def reload():
    """Replace the currently running instance of the script with a new one.

    AutoHotkey command: `Reload
    <https://www.autohotkey.com/docs/commands/Reload.htm>`_.
    """
    # TODO: If the new script has an error, AHK will show it and quit. Instead,
    # keep the old script running.
    # TODO: The "Reload This Script" tray menu item is broken.
    from . import launcher
    sys.exit(launcher.EXIT_CODE_RELOAD)


def output_debug(*objects, sep=" "):
    """Send *objects* separated by *sep* to the debugger with `OutputDebugString
    <https://docs.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-outputdebugstringw>`_.

    All non-keyword arguments are converted to strings with :func:`str()`.

    AutoHotkey command: `OutputDebug
    <https://www.autohotkey.com/docs/commands/OutputDebug.htm>`_.
    """
    if sep is None:
        # Python documentation for the print() function:
        #
        # > Both *sep* and *end* must be strings; they can also be `None`, which
        # > means to use the default values.
        sep = " "
    debug_str = sep.join(map(str, objects))
    ctypes.windll.kernel32.OutputDebugStringW(debug_str)


def coop(func, *args, **kwargs):
    """Run the given function in a new thread and make it cooperate with AHK's
    event loop.

    Use :func:`!coop` to execute **pre-existing** long-running I/O bound Python
    processes like HTTP servers and stdin readers that are designed to handle
    KeyboardInterrupt:

    .. code-block:: python

        import code
        import ahkpy as ahk
        ahk.coop(code.interact)

    The call starts a new thread and blocks the current thread until the
    function finishes. Returns the result of the function or raises the
    exception.

    Whenever :exc:`KeyboardInterrupt` occurs in the current thread, it's
    propagated to the background thread so it could stop.

    .. note::

        If you start your own threads, design them so that the main thread could
        stop them. For example, use :class:`~threading.Event` or
        :class:`~queue.Queue`.

        If you need to wait for the background thread to finish, don't call
        :meth:`threading.Thread.join` in the main thread. It blocks the handling
        of AHK message queue, that is, AHK won't be able to handle the hotkeys
        and other callbacks. Let AHK handle its message queue by calling
        :func:`sleep` repeatedly while checking that the background thread is
        alive:

        .. code-block:: python

            import threading
            th = threading.Thread(target=some_worker)
            th.start()
            # Avoid calling th.join()
            while th.is_alive():
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
