import sys

import pytest

import ahkpy as ahk


def test_hotkey_refcounts(request):
    func1 = lambda: None  # noqa: E731
    func2 = lambda: None  # noqa: E731
    func1_refcount = sys.getrefcount(func1)
    func2_refcount = sys.getrefcount(func2)

    hk = ahk.hotkey("F13", func1)
    request.addfinalizer(hk.disable)
    assert hk.key_name == "F13"
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount

    hk.update(func=func2)
    assert sys.getrefcount(func1) == func1_refcount
    assert sys.getrefcount(func2) == func2_refcount + 1

    hk.update(func=func1)
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount

    hk.update(func=func1)
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount

    hk2 = ahk.hotkey("F14", func1)
    request.addfinalizer(hk2.disable)
    assert sys.getrefcount(func1) == func1_refcount + 2
    assert sys.getrefcount(func2) == func2_refcount

    hk2.update(func=func2)
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount + 1


def test_exceptions():
    with pytest.raises(ValueError, match="key_name must not be blank"):
        ahk.hotkey(None)

    with pytest.raises(ValueError, match="key_name must not be blank"):
        ahk.hotkey("")

    with pytest.raises(TypeError, match="must be callable"):
        ahk.hotkey("^t", func="not callable")


def test_hotkey_field(request):
    hk = ahk.hotkey("F13", lambda: None)
    request.addfinalizer(hk.disable)
    assert hk.key_name == "F13"


def test_reenable_on_init(request):
    hk = ahk.hotkey("F13", lambda: None)
    request.addfinalizer(hk.disable)
    hk.disable()

    called = False

    @ahk.hotkey("F13")
    def hk2():
        nonlocal called
        called = True

    request.addfinalizer(hk2.disable)

    assert not called
    ahk.send("{F13}", level=1)
    ahk.sleep(0)
    assert called


def test_hotkeys_in_child_ahk(child_ahk):
    def hotkeys():
        import ahkpy as ahk
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.hotkey("F14")
        def show_msgbox():
            ahk.message_box("Hello from hotkey.")

        @ahk.hotkey("F15")
        def show_bang():
            1 / 0

        @ahk.hotkey("F16")
        def disable_ctrl_t():
            show_msgbox.disable()
            print("ok01")

        @ahk.hotkey("F17")
        def enable_ctrl_t():
            show_msgbox.enable()
            print("ok02")

        @ahk.hotkey("F18")
        def change_f14():
            show_msgbox.update(func=lambda: print("ok04"))
            print("ok03")

        print("ok00")

    proc = child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    msg_boxes = ahk.windows.filter(title="Python.ahk")
    assert not msg_boxes.get_active(text="Hello from hotkey")
    ahk.send("{F14}")
    assert msg_boxes.wait(text="Hello from hotkey", timeout=0.5)
    msg_boxes.first().send("{Space}")

    assert not msg_boxes.get_active(text="ZeroDivisionError")
    ahk.send("{F15}")
    assert msg_boxes.wait(text="ZeroDivisionError", timeout=0.5)

    msg_boxes.first().send("{Space}")
    assert msg_boxes.wait_close(text="ZeroDivisionError", timeout=1)

    ahk.send("{F16}")  # Disable {F14}
    child_ahk.wait(1)
    ahk.send("{F14}")
    assert not msg_boxes.wait(text="Hello from hotkey", timeout=0.5)

    ahk.send("{F17}")  # Enable {F14}
    child_ahk.wait(2)
    ahk.send("{F14}")
    assert msg_boxes.wait(text="Hello from hotkey", timeout=1)

    msg_boxes.first().send("{Space}")
    assert msg_boxes.wait_close(text="Hello from hotkey", timeout=1)

    ahk.send("{F18}")  # Change the handler of {F14} to print "ok04"
    child_ahk.wait(3)
    ahk.send("{F14}")
    assert not msg_boxes.wait(text="Hello from hotkey", timeout=0.5)
    child_ahk.wait(4)

    ahk.send("{F24}")
    child_ahk.close()
    assert "ZeroDivisionError:" in proc.stderr.read()
    assert proc.returncode == 0


def test_update_options(request):
    calls = []
    hk = ahk.hotkey("F13", calls.append, "F13")
    request.addfinalizer(hk.disable)
    ahk.send_event("{F13}", level=10)
    ahk.sleep(0)
    assert calls == ["F13"]

    calls.clear()
    hk.update(input_level=20)
    ahk.send_event("{F13}", level=10)
    ahk.sleep(0)
    assert calls == []

    ahk.send_event("{F13}", level=21)
    ahk.sleep(0)
    assert calls == ["F13"]


def test_hotkey_returns(child_ahk):
    def hotkeys():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", object)  # object() cannot be converted to an AHK value
        print("ok00")

    child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    ahk.send_event("{F13}", level=10)  # Must not raise an error
    assert not ahk.windows.wait(
        title="Python.ahk",
        text="Error:  cannot convert '<object object",
        timeout=0.1,
    )

    ahk.send("{F24}")
