import os
import time

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


def test_hotkey(child_ahk):
    with pytest.raises(ahk.Error, match="invalid key name"):
        ahk.hotkey("")

    with pytest.raises(TypeError, match="must be callable"):
        ahk.hotkey("^t", func="not callable")

    child_ahk.popen_code("""\
        import ahk

        @ahk.hotkey("^t")
        def show_msgbox():
            print("ok01")
            ahk.message_box("Hello from hotkey.")

        @ahk.hotkey("^y")
        def show_bang():
            print("ok02")
            1 / 0

        print("ok00")
        """)

    child_ahk.wait()

    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") == 0
    ahk.send("^t")
    child_ahk.wait()
    time.sleep(.01)
    assert ahk.win_active("EmbedPython.ahk", "Hello from hotkey") != 0
    ahk.send("{Space}")

    assert ahk.win_active("EmbedPython.ahk", "ZeroDivisionError") == 0
    ahk.send("^y")
    child_ahk.wait()
    assert ahk.win_active("EmbedPython.ahk", "ZeroDivisionError") != 0
    ahk.send("{Space}")

    child_ahk.close()
    assert "ZeroDivisionError:" in child_ahk.proc.stderr.read()


def test_get_key_state():
    ahk.message_box("Press LShift.")
    if ahk.get_key_state("LShift"):
        ahk.message_box("LShift is pressed")
    else:
        ahk.message_box("LShift is not pressed")


def test_timer(child_ahk):
    timer = ahk.set_timer(lambda: None, countdown=1)
    with pytest.raises(AttributeError, match="can't set attribute"):
        timer.func = None

    timer.delete()
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
    assert res.returncode == 0

    res = child_ahk.run_code("""\
        import sys, ahk

        ahk.hotkey("^t", lambda: None)  # Make the script persistent

        @ahk.set_timer(period=0.1)
        def ding():
            print("Ding!")
            ding.disable()

        @ahk.set_timer(countdown=0.5)
        def exit():
            sys.exit()
        """)
    assert res.stdout == "Ding!\n"
    assert res.returncode == 0
