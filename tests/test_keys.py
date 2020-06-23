from textwrap import dedent

import pytest

import _ahk  # noqa
import ahk


def test_get_key_state(child_ahk):
    with pytest.raises(ValueError, match="key_name is invalid or the state of the key could not be determined"):
        ahk.get_key_state("beep")

    assert ahk.get_key_state("F13") is False
    ahk.send("{F13 Down}")
    assert ahk.get_key_state("F13") is True
    ahk.send("{F13 Up}")
    assert ahk.get_key_state("F13") is False


def test_is_key_toggled():
    with pytest.raises(ValueError, match="key_name must be one of"):
        ahk.is_key_toggled("F13")

    initial_state = ahk.is_key_toggled("CapsLock")
    assert isinstance(initial_state, bool)
    ahk.set_caps_lock_state(True)
    assert ahk.is_key_toggled("CapsLock") is True
    ahk.set_caps_lock_state(False)
    assert ahk.is_key_toggled("CapsLock") is False
    ahk.set_caps_lock_state(initial_state)


def test_hotkey(child_ahk):
    with pytest.raises(ahk.Error, match="invalid key name"):
        ahk.hotkey("")

    with pytest.raises(TypeError, match="must be callable"):
        ahk.hotkey("^t", func="not callable")

    hk = ahk.hotkey("F13", lambda: None)
    assert hk.key_name == "F13"
    hk.disable()

    def hotkeys():
        import ahk
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

        print("ok00")

    child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    msg_boxes = ahk.windows.filter(title="EmbedPython.ahk")
    assert not msg_boxes.get_active(text="Hello from hotkey")
    ahk.send("{F14}")
    assert msg_boxes.wait(text="Hello from hotkey", timeout=0.5)
    msg_boxes.send("{Space}")

    assert not msg_boxes.get_active(text="ZeroDivisionError")
    ahk.send("{F15}")
    assert msg_boxes.wait(text="ZeroDivisionError", timeout=0.5)
    msg_boxes.send("{Space}")

    assert not msg_boxes.get_active()
    ahk.send("{F16}")  # Disable {F14}
    child_ahk.wait(1)
    ahk.send("{F14}")
    assert not msg_boxes.wait(text="Hello from hotkey", timeout=0.5)

    ahk.send("{F17}")  # Enable {F14}
    child_ahk.wait(2)
    ahk.send("{F14}")
    assert msg_boxes.wait(text="Hello from hotkey", timeout=0.5)

    ahk.send("{F24}")
    child_ahk.close()
    assert "ZeroDivisionError:" in child_ahk.proc.stderr.read()
    assert child_ahk.proc.returncode == 0


def test_hotkey_context(child_ahk):
    def code():
        import ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", lambda: ahk.message_box("Beep"))
        with ahk.hotkey_context(lambda: ahk.windows.get_active(exe="AutoHotkey.exe", text="Beep")):
            ahk.hotkey("F13", lambda: ahk.message_box("Boop"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)

    beep_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Beep")
    boop_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Boop")

    ahk.send("{F13}")
    assert beep_windows.wait(timeout=1)
    assert not boop_windows.exist()

    ahk.send("{F13}")
    assert boop_windows.wait(timeout=1)
    assert beep_windows.exist()

    ahk.send("{F24}")


def test_failing_hotkey_context(child_ahk):
    def code():
        import ahk
        with ahk.hotkey_context(lambda: ahk.windows.get_active(class_name="Shell_TrayWnd")):
            ahk.hotkey("F13", lambda: ahk.message_box("Boop"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)

    boop_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Boop")

    ahk.send("{F13}")
    assert not boop_windows.wait(timeout=0.1)

    ahk.windows.activate(class_name="Shell_TrayWnd")
    ahk.send("{F13}")
    with pytest.xfail():
        assert boop_windows.wait(timeout=1)

    ahk.send("{F24}")


def test_key_wait(child_ahk):
    def code():
        import ahk
        import sys

        print("ok00")
        result = ahk.key_wait_pressed("RShift")
        assert result is True, "result must be True"
        print("ok01")
        result = ahk.key_wait_released("RShift")
        assert result is True, "result must be True"
        print("ok02")

        result = ahk.key_wait_pressed("RShift", timeout=.1)
        assert result is False, "result must be False"
        print("ok03")

        sys.exit()

    child_ahk.popen_code(code)

    child_ahk.wait(0)
    ahk.send("{RShift Down}")
    child_ahk.wait(1)
    ahk.send("{RShift Up}")
    child_ahk.wait(2)

    child_ahk.wait(3)
    child_ahk.close()
    assert child_ahk.proc.returncode == 0


def test_send_level(child_ahk):
    with pytest.raises(ValueError, match="level must be between 0 and 100"):
        ahk.send_level(-1)
    with pytest.raises(ValueError, match="level must be between 0 and 100"):
        ahk.send_level(101)

    called = False

    @ahk.hotkey("F15", input_level=10)
    def f15():
        nonlocal called
        called = True

    ahk.send("{F15}")
    ahk.sleep(0)  # Let AHK process the hotkey.
    assert not called

    ahk.send_level(20)
    ahk.send("{F15}")
    ahk.sleep(0)
    assert called

    ahk.send_level(0)

    def code():
        import ahk
        import _ahk  # noqa

        @ahk.set_timer(countdown=0.1)
        def beep():
            print("beep", _ahk.call("A_SendLevel"), flush=True)
            ahk.send_level(20)
            print("beep", _ahk.call("A_SendLevel"), flush=True)

        @ahk.set_timer(countdown=0.2)
        def boop():
            print("boop", _ahk.call("A_SendLevel"), flush=True)

        ahk.send_level(10)
        print("main", _ahk.call("A_SendLevel"), flush=True)
        ahk.sleep(0.3)

    proc = child_ahk.run_code(code)
    assert proc.stdout == dedent("""\
        main 10
        beep 10
        beep 20
        boop 10
        """)
    assert proc.stderr == ""
    assert proc.returncode == 0

    # TODO: SendLevel and friends must be thread-local in Python.
    def threaded():
        import ahk
        import _ahk  # noqa
        import threading

        def beep():
            print("beep", _ahk.call("A_SendLevel"), flush=True)
            ahk.send_level(20)
            print("beep", _ahk.call("A_SendLevel"), flush=True)

        threading.Timer(0.1, beep).start()

        def boop():
            print("boop", _ahk.call("A_SendLevel"), flush=True)

        threading.Timer(0.2, boop).start()

        ahk.send_level(10)
        print("main", _ahk.call("A_SendLevel"), flush=True)
        ahk.sleep(0.3)

    proc = child_ahk.run_code(threaded)
    with pytest.xfail():
        assert proc.stdout == dedent("""\
            main 10
            beep 10
            beep 20
            boop 10
            """)
    assert proc.stderr == ""
    assert proc.returncode == 0
