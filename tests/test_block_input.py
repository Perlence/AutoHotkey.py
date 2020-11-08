import ctypes

import pytest

import ahkpy as ahk


skip_unless_admin = pytest.mark.skipif(
    not ctypes.windll.shell32.IsUserAnAdmin(),
    reason="This test requires admin permissions",
)


@skip_unless_admin
def test_block_input(child_ahk):
    def hotkeys():
        import ahkpy as ahk
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.hotkey("F15")
        def block():
            with ahk.block_input():
                ahk.sleep(0.1)
            print("ok01")

        print("ok00")

    child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    ahk.send("{F15}")
    x, y = ahk.get_mouse_pos()
    ahk.mouse_move(100, 100, relative_to="cursor", mode="event")
    assert ahk.get_mouse_pos() == (x, y)
    child_ahk.wait(1)

    x, y = ahk.get_mouse_pos()
    ahk.mouse_move(100, 100, relative_to="cursor", mode="event")
    assert ahk.get_mouse_pos() == (x+100, y+100)

    ahk.mouse_move(-100, -100, relative_to="cursor", mode="event")

    ahk.send("{F24}")


@skip_unless_admin
def test_block_input_while_sending(child_ahk, notepad):
    def hotkeys():
        import ahkpy as ahk
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.hotkey("F15")
        def block():
            with ahk.block_input_while_sending():
                print("ok01")
                ahk.mouse_move(100, 100, relative_to="cursor", mode="event")
                ahk.mouse_move(-100, -100, relative_to="cursor", mode="event")
            print("ok02")

        print("ok00")

    child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    edit = notepad.get_control("Edit1")

    ahk.send("{F15}")
    child_ahk.wait(1)
    ahk.sleep(0.1)
    ahk.send("{Text}Hello!")
    assert edit.text == ""
    child_ahk.wait(2)

    ahk.send("{Text}Hello!")
    ahk.sleep(0.1)
    assert edit.text == "Hello!"

    ahk.send("{F24}")
