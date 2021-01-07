import os

import ahkpy as ahk


def test_message_box_func(child_ahk, settings):
    def msg_boxes_code():
        import ahkpy as ahk
        ahk.message_box()
        ahk.message_box("Hello, мир!")
        ahk.message_box("Hello, 世界")
        ahk.message_box("Do you want to continue? (Press YES or NO)", buttons="yes_no")

    child_ahk.popen_code(msg_boxes_code)
    settings.win_delay = 0

    msg_boxes = ahk.windows.filter(title="Python.ahk")

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


def test_message_box_show(request):
    result = ahk.MessageBox().show(timeout=0.01)
    assert result is None

    msg_boxes = ahk.windows.filter(pid=os.getpid())
    t = ahk.set_timer(0.1, lambda: msg_boxes.wait(timeout=0.1).get_control("Button1").check())
    request.addfinalizer(t.stop)
    result = ahk.MessageBox().show()
    assert result == "ok"

    t.update(func=lambda: msg_boxes.wait(text="Huh?", timeout=0.1).get_control("Button2").check())
    result = ahk.MessageBox("What?", buttons="yes_no").show("Huh?")
    assert result == "no"


def test_message_box_staticmethod(request):
    msg_boxes = ahk.windows.filter(pid=os.getpid())
    t = ahk.set_timer(0.1, lambda: msg_boxes.wait(timeout=0.1).get_control("Button1").check())
    request.addfinalizer(t.stop)
    result = ahk.MessageBox.info("Info")
    assert result == "ok"

    t.update(func=lambda: msg_boxes.wait(timeout=0.1).get_control("Button1").check())
    result = ahk.MessageBox.ok_cancel("Continue?")
    assert result is True

    t.update(func=lambda: msg_boxes.wait(timeout=0.1).get_control("Button2").check())
    result = ahk.MessageBox("What?", buttons="yes_no").show()
    assert result == "no"
