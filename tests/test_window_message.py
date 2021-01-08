import os
import sys

import pytest

import ahkpy as ahk


def test_on_message(request):
    args = ()

    @ahk.on_message(0x5555)
    def handler(w_param, l_param, msg, hwnd):
        nonlocal args
        args = (w_param, l_param, msg, hwnd)
        return 42

    request.addfinalizer(handler.unregister)

    win = ahk.all_windows.first(pid=os.getpid())
    assert win
    result = win.send_message(0x5555, 0, 99)
    assert result == 42
    assert args == (0, 99, 0x5555, win.id)

    bare_handler_called = False

    @ahk.on_message(0x5556)
    def bare_handler():
        nonlocal bare_handler_called
        bare_handler_called = True
        return None

    result = win.send_message(0x5556, 0, 99)
    assert result == 0
    assert bare_handler_called

    result = win.post_message(0x5556, 0, 99)
    assert result is True

    handler_func = handler.func
    handler_func_refcount = sys.getrefcount(handler_func)
    handler.unregister()
    assert sys.getrefcount(handler_func) == handler_func_refcount - 1

    result = win.send_message(0x5555, 0, 99)
    assert result == 0


def test_on_message_timeout(child_ahk):
    def code():
        import ahkpy as ahk
        import os
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.on_message(0x5555)
        def slow_handler():
            ahk.sleep(1)
            return 42

        print(os.getpid())

    proc = child_ahk.popen_code(code)
    ahk_pid = int(proc.stdout.readline().strip())

    win = ahk.all_windows.first(pid=ahk_pid)
    with pytest.raises(ahk.Error, match="response timed out"):
        win.send_message(0x5555, 0, 99, timeout=0.1)

    ahk.send("{F24}")
    child_ahk.close()
    assert proc.stdout.read() == ""
    assert proc.stderr.read() == ""
    assert proc.returncode == 0
