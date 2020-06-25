import os

import pytest

import ahk


def test_message_box(child_ahk):
    def msg_boxes_code():
        import ahk
        ahk.message_box()
        ahk.message_box("Hello, мир!")
        ahk.message_box("Hello, 世界")
        ahk.message_box("Do you want to continue? (Press YES or NO)", options=4)

    child_ahk.popen_code(msg_boxes_code)
    ahk.set_win_delay(None)

    msg_boxes = ahk.windows.filter(exe="AutoHotkey.exe")

    msg_box = msg_boxes.wait_active(text="Press OK to continue", timeout=1)
    assert msg_box
    msg_box.send("{Enter}")

    msg_box = msg_boxes.wait_active(text="Hello, мир!", timeout=1)
    assert msg_box
    msg_box.send("{Enter}")

    msg_box = msg_boxes.wait_active(text="Hello, 世界", timeout=1)
    assert msg_box
    msg_box.send("{Enter}")

    msg_box = msg_boxes.wait_active(text="Do you want to continue? (Press YES or NO)", timeout=1)
    assert msg_box
    assert "&Yes" in msg_box.text
    assert "&No" in msg_box.text
    msg_box.send("{Enter}")


def test_on_message(detect_hidden_windows):
    args = ()

    @ahk.on_message(0x5555)
    def handler(w_param, l_param, msg, hwnd):
        # TODO: handler() takes 2 positional arguments but 4 were given
        nonlocal args
        args = (w_param, l_param, msg, hwnd)
        return 42

    win = ahk.windows.first(pid=os.getpid())
    result = win.send_message(0x5555, 0, 99)
    assert result == 42
    assert args == (0, 99, 0x5555, win.id)

    @ahk.on_message(0x5556)
    def null_handler(w_param, l_param, msg, hwnd):
        return None

    result = win.send_message(0x5556, 0, 99)
    assert result == 0

    result = win.post_message(0x5556, 0, 99)
    assert result is True

    not_win = ahk.Window(99999)
    assert not not_win.exists
    with pytest.raises(RuntimeError, match="there was a problem sending message"):
        not_win.send_message(0x5555, 0, 99)


def test_on_message_timeout(child_ahk, detect_hidden_windows):
    def code():
        import ahk
        import sys

        ahk.hotkey("F24", lambda: sys.exit())

        @ahk.on_message(0x5555)
        def slow_handler(w_param, l_param, msg, hwnd):
            ahk.sleep(1)
            return 42

        print("ok00")

    proc = child_ahk.popen_code(code)
    child_ahk.wait(0)

    win = ahk.windows.first(pid=proc.pid)
    with pytest.raises(RuntimeError, match="response timed out"):
        win.send_message(0x5555, 0, 99, timeout=0.1)

    ahk.send("{F24}")
    child_ahk.close()
    assert proc.stdout.read() == ""
    assert proc.stderr.read() == ""
    assert proc.returncode == 0
