import ctypes
import functools
import inspect
import queue
import sys
import threading
import time

import _ahk

__all__ = [
    "coop",
    "output_debug",
    "poll",
    "restart",
    "resume",
    "sleep",
    "suspend",
    "toggle_suspend",
]


global_ahk_lock = threading.RLock()


def ahk_call(cmd: str, *args):
    """Call the arbitrary AHK command/function *cmd* with *args* arguments.

    Use this function when there's no appropriate AutoHotkey.py API.
    """
    locked = global_ahk_lock.acquire(timeout=1)
    if not locked:
        if threading.current_thread() is threading.main_thread():
            err = RuntimeError(
                "deadlock occurred; the main thread tried calling AHK "
                "when it was acquired by another thread",
            )
            # Don't show the message box with an error via AHK.
            err._ahk_silent_exc = True
            raise err
        global_ahk_lock.acquire()
    try:
        return _ahk.call(cmd, *args)
    finally:
        global_ahk_lock.release()


def sleep(secs):
    """Suspend execution of the calling thread for the given number of seconds.

    During the wait, AHK checks its message queue and handles hotkeys and other
    callbacks.

    :command: `Sleep <https://www.autohotkey.com/docs/commands/Sleep.htm>`_
    """
    if not isinstance(secs, (int, float)):
        raise TypeError(f"a number is required (got type {secs.__class__.__name__})")
    _wait_for(secs, None)


def _wait_for(secs, check_fn):
    if secs is None:
        secs = float("inf")

    if secs < 0:
        raise ValueError("sleep length must be non-negative")
    elif secs <= _poll_interval:
        time.sleep(secs)
        poll()
        return check_fn and check_fn()
    else:
        stop = time.perf_counter() + secs
        while time.perf_counter() < stop:
            time.sleep(_poll_interval)
            poll()
            result = check_fn and check_fn()
            if result:
                return result


# The interval between AHK message queue polls during the blocking operations.
_poll_interval = 0.01


def poll():
    """Make AHK check its the message queue.

    This can be used to force any pending interruptions to occur at a specific
    place rather than somewhere more random.
    """
    ahk_call("Sleep", -1)


def suspend():
    """Disable all hotkeys and hotstrings.

    :command: `Suspend, On
       <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
    """
    ahk_call("Suspend", "On")


def resume():
    """Enable all hotkeys and hotstrings.

    :command: `Suspend, Off
       <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
    """
    ahk_call("Suspend", "Off")


def toggle_suspend():
    """Toggle all hotkeys and hotstrings.

    :command: `Suspend, Toggle
       <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
    """
    ahk_call("Suspend", "Toggle")


def restart():
    """Terminate the currently running instance of the script and start a new
    one.

    :command: `Reload <https://www.autohotkey.com/docs/commands/Reload.htm>`_
    """
    # TODO: If the new script has an error, AHK will show it and quit. Instead,
    # keep the old script running.
    from . import launcher
    sys.exit(launcher.EXIT_CODE_RESTART)


def output_debug(*objects, sep=" "):
    """Send *objects* separated by *sep* to the debugger with `OutputDebugString
    <https://docs.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-outputdebugstringw>`_.

    All non-keyword arguments are converted to strings with :class:`str()
    <str>`.

    :command: `OutputDebug
       <https://www.autohotkey.com/docs/commands/OutputDebug.htm>`_
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

    Use :func:`!coop` to execute long-running I/O bound Python processes like
    HTTP servers and stdin readers that are designed to handle
    :exc:`KeyboardInterrupt`::

        import code
        ahkpy.coop(code.interact)

    This call runs the given function in a new thread and waits for the function
    to finish. Returns the function result or raises the exception.

    Whenever :exc:`KeyboardInterrupt` occurs in the main thread, it's propagated
    to the background thread so it could stop.

    Calling :func:`!coop` from a background thread doesn't start a new one.
    Instead, the given function is executed in the current thread.
    """
    if threading.current_thread() is not threading.main_thread():
        # Just execute the function, we are already in another thread.
        return func(*args, **kwargs)

    q = queue.SimpleQueue()
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
            sleep(_poll_interval)
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


def void(func):
    """Create a wrapper that calls *func* and returns nothing."""
    def void_wrapper(*args):
        func(*args)
    return void_wrapper


def _wrap_callback(func, arg_names, bare_cb, keyword_cb):
    try:
        signature = inspect.signature(func)
    except ValueError:
        # Usually ctypes functions.
        return functools.partial(bare_cb, func)

    missing_args = set()
    for arg_name in arg_names:
        try:
            signature.bind_partial(**{arg_name: None})
        except TypeError:
            missing_args.add(arg_name)

    # There must be either all arg_names in the func signature, or no arg_names.
    # Specifying only a part of arg_names raises a TypeError. All or nothing.
    if not missing_args:
        return functools.partial(keyword_cb, func)
    if missing_args == set(arg_names):
        signature.bind()  # Check required arguments
        return functools.partial(bare_cb, func)
    else:
        msg = f"the following keyword arguments are missing: {', '.join(missing_args)}"
        raise TypeError(msg)
