import dataclasses as dc
import functools
import weakref
from typing import Callable, Optional

from .flow import ahk_call

__all__ = [
    "Timer",
    "set_countdown",
    "set_timer",
]


def set_timer(interval=0.25, func=None, *args, priority=0):
    """Create a :class:`Timer` that will run *func* periodically with arguments
    *args* after *interval* seconds have passed.

    If you want the *func* to be called with keyword arguments use
    :func:`functools.partial`.

    The optional parameter *priority* is an integer between -2147483648 and
    2147483647.

    This function can be used as a decorator:

    .. code-block:: python

        @ahkpy.set_timer(1)
        def handler():
            print("tick")

        assert isinstance(handler, ahkpy.Timer)

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
    """Create a :class:`Timer` that will run *func* once with arguments *args*
    after *interval* seconds have passed.

    If you want the *func* to be called with keyword arguments use
    :func:`functools.partial`.

    The optional parameter *priority* is an integer between -2147483648 and
    2147483647.

    This function can be used as a decorator:

    .. code-block:: python

        @ahkpy.set_countdown(1)
        def handler():
            print("boom")

        assert isinstance(handler, ahkpy.Timer)

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
    """This object represents an action that should be run after a certain
    amount of time has passed.

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

        If the *interval*, *priority*, or *periodic* arguments are given, the
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
