import os
import time
from textwrap import dedent

import pytest

import _ahk  # noqa
import ahk


# TODO: sys.stdout is not in utf-8.


def test_call():
    with pytest.raises(TypeError, match="missing 1 required"):
        _ahk.call()

    with pytest.raises(ahk.Error, match="unknown function"):
        _ahk.call("NoSuchFunction")

    os.environ["HELLO"] = "Привет"
    hello = _ahk.call("EnvGet", "HELLO")
    assert hello == os.environ["HELLO"]

    temp = _ahk.call("EnvGet", "TEMP")
    assert isinstance(temp, str), "EnvGet result must be a string"

    rnd = _ahk.call("Random", 42, "42")
    assert isinstance(rnd, int), "Random result must be an integer"
    assert rnd == 42, f"Result must be 42, got {rnd}"

    assert _ahk.call("Random", 1, True) == 1, "Result must be 1"

    val = _ahk.call("Max", 9223372036854775807)
    assert val == 9223372036854775807, f"Result must be 9223372036854775807, got {val}"

    val = _ahk.call("Min", -9223372036854775806)
    assert val == -9223372036854775806, f"Result must be -9223372036854775806, got {val}"

    with pytest.raises(OverflowError, match="too big to convert"):
        val = _ahk.call("Max", 9223372036854775808)

    val = _ahk.call("Min", 0.5)
    assert val == 0.5, f"Result must be 0.5, got {val}"

    with pytest.raises(ahk.Error, match="cannot convert '<object object"):
        _ahk.call("Min", object())

    with pytest.raises(NotImplementedError, match="cannot convert AHK object"):
        _ahk.call("Func", "Main")


def test_message_box():
    result = ahk.message_box()
    assert result == "", "MsgBox result must be an empty string"
    ahk.message_box("Hello, мир!")
    ahk.message_box("Do you want to continue? (Press YES or NO)", options=4)


def test_get_key_state():
    ahk.message_box("Press LShift.")
    if ahk.get_key_state("LShift"):
        ahk.message_box("LShift is pressed")
    else:
        ahk.message_box("LShift is not pressed")


def test_hotkey(child_ahk):
    with pytest.raises(ahk.Error, match="invalid key name"):
        ahk.hotkey("")

    with pytest.raises(TypeError, match="must be callable"):
        ahk.hotkey("^t", func="not callable")

    hk = ahk.hotkey("F13", lambda: None)
    assert hk.key_name == "F13"

    child_ahk.popen_code("""\
        import ahk
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.hotkey("F14")
        def show_msgbox():
            print("ok01")
            ahk.message_box("Hello from hotkey.")

        @ahk.hotkey("F15")
        def show_bang():
            print("ok02")
            1 / 0

        @ahk.hotkey("F16")
        def disable_ctrl_t():
            show_msgbox.disable()
            print("ok03")

        @ahk.hotkey("F17")
        def enable_ctrl_t():
            show_msgbox.enable()
            print("ok04")

        print("ok00")
        """)

    child_ahk.wait(0)

    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") == 0
    ahk.send("{F14}")
    child_ahk.wait(1)
    time.sleep(.01)
    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") != 0
    ahk.send("{Space}")

    assert ahk.win_active("EmbedPython.ahk", "ZeroDivisionError") == 0
    ahk.send("{F15}")
    child_ahk.wait(2)
    time.sleep(.01)
    assert ahk.win_active("EmbedPython.ahk", "ZeroDivisionError") != 0
    ahk.send("{Space}")

    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") == 0
    ahk.send("{F16}")  # Disable {F14}
    child_ahk.wait(3)
    ahk.send("{F14}")
    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") == 0

    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") == 0
    ahk.send("{F17}")  # Enable {F14}
    child_ahk.wait(4)
    ahk.send("{F14}")
    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") != 0

    ahk.send("{F24}")
    child_ahk.close()
    assert "ZeroDivisionError:" in child_ahk.proc.stderr.read()
    assert child_ahk.proc.returncode == 0


def test_key_wait(child_ahk):
    child_ahk.popen_code("""\
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
        """)

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

    proc = child_ahk.run_code("""\
        import ahk, _ahk

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
        """)
    assert proc.stdout == dedent("""\
        main 10
        beep 10
        beep 20
        boop 10
        """)
    assert proc.stderr == ""
    assert proc.returncode == 0


def test_sleep(child_ahk):
    proc = child_ahk.run_code("""\
        import ahk
        timer = ahk.set_timer(lambda: print(1), countdown=0.1)
        ahk.sleep(0.2)  # sleep longer than the countdown
        print(2)
        # sys.exit()
        # ahk.message_box(2)
        # 1/0
        """)
    assert proc.stdout == "1\n2\n"
    assert proc.stderr == ""
    assert proc.returncode == 0

    proc = child_ahk.run_code("""\
        import ahk
        import threading
        timer = ahk.set_timer(lambda: print(1), countdown=0.1)
        threading.Timer(0.2, lambda: print(2)).start()
        ahk.sleep(0.3)
        print(3)
        """)
    assert proc.stdout == "1\n2\n3\n"
    assert proc.stderr == ""
    assert proc.returncode == 0


def test_timer(child_ahk):
    timer = ahk.set_timer(lambda: None, countdown=1)
    with pytest.raises(AttributeError, match="can't set attribute"):
        timer.func = None

    timer.cancel()
    del timer

    res = child_ahk.run_code("""\
        import sys, ahk

        ahk.hotkey("^t", lambda: None)  # Make the script persistent

        @ahk.set_timer(countdown=0.1)
        def dong():
            print("Dong!")
            sys.exit()

        print("Ding!")
        """)
    assert res.stdout == "Ding!\nDong!\n"
    assert res.stderr == ""
    assert res.returncode == 0

    res = child_ahk.run_code("""\
        import sys, ahk

        ahk.hotkey("^t", lambda: None)  # Make the script persistent

        @ahk.set_timer(period=0.1)
        def ding():
            print("Ding!")
            ding.stop()

        @ahk.set_timer(countdown=0.5)
        def exit():
            sys.exit()
        """)
    assert res.stdout == "Ding!\n"
    assert res.stderr == ""
    assert res.returncode == 0
