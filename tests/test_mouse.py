import pytest

import ahkpy as ahk


def test_click_validation():
    with pytest.raises(ValueError, match="'nooo' is not a valid mouse button"):
        ahk.click("nooo")
    with pytest.raises(TypeError, match="'<' not supported"):
        ahk.click(times=[])
    with pytest.raises(ValueError, match="must be positive"):
        ahk.click(times=-1)
    with pytest.raises(ValueError, match=r"'[$@%]{3}' is not a valid modifier"):
        ahk.click(modifier="!@#$%")


def test_click(child_ahk, settings):
    def hotkeys():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("LButton", print, "ok01")
        ahk.hotkey("RButton", print, "ok02")
        ahk.hotkey("+LButton", print, "ok03")
        ahk.hotkey("WheelDown", print, "ok04")
        ahk.hotkey("WheelLeft", print, "ok05")
        print("ok00")

    child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    settings.send_level = 10

    ahk.click()
    child_ahk.wait(1)

    ahk.click("right")
    child_ahk.wait(2)

    ahk.right_click()
    child_ahk.wait(2)

    ahk.click(times=2)
    child_ahk.wait(1)
    child_ahk.wait(1)

    ahk.double_click()
    child_ahk.wait(1)
    child_ahk.wait(1)

    ahk.click("left", modifier="+")
    child_ahk.wait(3)

    ahk.send("{Shift Down}")
    ahk.click("left")
    child_ahk.wait(3)
    ahk.send("{Shift Up}")

    ahk.mouse_scroll("down")
    child_ahk.wait(4)

    ahk.mouse_scroll("down", 2)
    child_ahk.wait(4)
    child_ahk.wait(4)

    ahk.mouse_scroll("left")
    child_ahk.wait(5)

    ahk.send("{F24}")


def test_move():
    with pytest.raises(ValueError, match="'nooo' is not a valid coord mode"):
        ahk.mouse_move(0, 0, relative_to="nooo")


def test_get_mouse_pos(notepad):
    ahk.mouse_move(x=0, y=0, relative_to="window")
    x, y = ahk.get_mouse_pos(relative_to="screen")
    assert notepad.x == x
    assert notepad.y == y

    win = ahk.get_window_under_mouse()
    assert win == notepad

    ahk.mouse_move(x=100, y=100, relative_to="window")
    ahk.click()
    ctl = ahk.get_control_under_mouse()
    assert ctl
    assert ctl.class_name == "Edit"
