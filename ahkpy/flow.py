import ctypes
import queue
import sys
import threading

import _ahk

__all__ = [
    "coop",
    "output_debug",
    "reload",
    "resume",
    "sleep",
    "suspend",
    "toggle_suspend",
]


global_ahk_lock = threading.RLock()


def ahk_call(cmd: str, *args):
    """Call the arbitrary AHK command/function *cmd* with *args* arguments.

    Use this function when there's no appropriate AutoHotkey.py API.

    .. note::

       Calling blocking AHK functions from the background thread deadlocks the
       program::

           def bg_thread():
               ahk.wait_key_pressed("F1")
               # ^^ Blocks the thread until F1 is pressed
               print("F1 pressed")

           th = threading.Thread(target=bg_thread, daemon=True)
           th.start()
           while th.is_alive():
               ahk.sleep(0.01)

       Instead, use their nonblocking versions and yield control to other Python
       threads with :func:`time.sleep`::

           def bg():
               while not ahk.is_key_pressed("F1"):
                   time.sleep(0)
               print("F1 pressed")
    """
    # AHK callbacks are not reentrant. While the main thread is busy executing
    # an AHK function, trying to call another AHK function from another thread
    # leads to unpredictable results like program crash. The following lock
    # allows only one system thread to call AHK.
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
    if secs < 0:
        raise ValueError("sleep length must be non-negative")
    elif secs == 0:
        # TODO: Should it be -1 or 0?
        ahk_call("Sleep", -1)
    else:
        ahk_call("Sleep", int(secs * 1000))


def suspend():
    """Disable all hotkeys and hotstrings.

    :command: `Suspend <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
    """
    ahk_call("Suspend", "On")


def resume():
    """Enable all hotkeys and hotstrings.

    :command: `Suspend <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
    """
    ahk_call("Suspend", "Off")


def toggle_suspend():
    """Toggle all hotkeys and hotstrings.

    :command: `Suspend <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
    """
    ahk_call("Suspend", "Toggle")


def reload():
    """Replace the currently running instance of the script with a new one.

    :command: `Reload <https://www.autohotkey.com/docs/commands/Reload.htm>`_
    """
    # TODO: If the new script has an error, AHK will show it and quit. Instead,
    # keep the old script running.
    # TODO: The "Reload This Script" tray menu item is broken.
    from . import launcher
    sys.exit(launcher.EXIT_CODE_RELOAD)


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

    .. TODO: Move the following section to the user's guide.

    .. note::

       If you need to wait for the background thread to finish, calling
       :meth:`threading.Thread.join` in the main thread will block the handling
       of the AHK message queue. That is, AHK won't be able to handle the
       hotkeys and other callbacks. Let AHK handle its message queue by calling
       :func:`ahkpy.sleep` repeatedly while checking that the background thread
       is alive::

           import threading
           th = threading.Thread(target=some_worker)
           th.start()
           while th.is_alive():
               ahkpy.sleep(0.01)
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
