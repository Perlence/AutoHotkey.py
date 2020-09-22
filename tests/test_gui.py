import os

import pytest

import ahkpy as ahk


def test_message_box(child_ahk, settings):
    def msg_boxes_code():
        import ahkpy as ahk
        ahk.message_box()
        ahk.message_box("Hello, мир!")
        ahk.message_box("Hello, 世界")
        ahk.message_box("Do you want to continue? (Press YES or NO)", options=4)

    child_ahk.popen_code(msg_boxes_code)
    settings.win_delay = 0

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


def test_on_message(request):
    args = ()

    @ahk.on_message(0x5555)
    def handler(w_param, l_param, msg, hwnd):
        # TODO: handler() takes 2 positional arguments but 4 were given
        nonlocal args
        args = (w_param, l_param, msg, hwnd)
        return 42

    request.addfinalizer(handler.unregister)

    win = ahk.all_windows.first(pid=os.getpid())
    assert win
    result = win.send_message(0x5555, 0, 99)
    assert result == 42
    assert args == (0, 99, 0x5555, win.id)

    null_handler_called = False

    @ahk.on_message(0x5556)
    def null_handler(w_param, l_param, msg, hwnd):
        nonlocal null_handler_called
        null_handler_called = True
        return None

    result = win.send_message(0x5556, 0, 99)
    assert result == 0
    assert null_handler_called

    result = win.post_message(0x5556, 0, 99)
    assert result is True

    handler.unregister()
    result = win.send_message(0x5555, 0, 99)
    assert result == 0


def test_on_message_timeout(child_ahk):
    def code():
        import ahkpy as ahk
        import os
        import sys

        ahk.hotkey("F24", lambda: sys.exit())

        @ahk.on_message(0x5555)
        def slow_handler(w_param, l_param, msg, hwnd):
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


class TestTooltip:
    def test_basic(self, request):
        tooltip_windows = ahk.windows.filter(class_name="tooltips_class32", exe="AutoHotkey.exe")
        assert not tooltip_windows.exist()

        t1 = ahk.ToolTip()
        request.addfinalizer(t1.hide)
        t1.show("hello", 0, 0)
        assert tooltip_windows.exist()

        t1.hide()
        assert not tooltip_windows.exist()

    def test_exceptions(self, request):
        with pytest.raises(ValueError, match="text must not be empty"):
            ahk.ToolTip().show()

        with pytest.raises(ValueError, match="is not a valid coord mode"):
            ahk.ToolTip(relative_to="nooo")

    def test_too_many_tooltips(self, request):
        tooltips = []
        for i in range(1, 21):
            t = ahk.ToolTip(i, relative_to="screen")
            request.addfinalizer(t.hide)
            t.show(x=50*i, y=50*i)
            tooltips.append(t)

        with pytest.raises(RuntimeError, match="cannot show more than 20 tooltips"):
            ahk.ToolTip().show("21")
