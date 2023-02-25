import ahkpy as ahk


def test_hotkey_context(child_ahk):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", ahk.message_box, "Beep")
        ctx = ahk.HotkeyContext(lambda: ahk.windows.get_active(title="Python.ahk", text="Beep"))
        ctx.hotkey("F13", ahk.message_box, "Boop")
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)

    beep_windows = ahk.windows.filter(title="Python.ahk", text="Beep")
    boop_windows = ahk.windows.filter(title="Python.ahk", text="Boop")

    ahk.send("{F13}")
    assert beep_windows.wait(timeout=1)
    assert not boop_windows.exist()

    ahk.send("{F13}")
    assert boop_windows.wait(timeout=1)
    assert beep_windows.exist()

    ahk.send("{F24}")


def test_only_hotkey_context(child_ahk, settings):
    def code():
        import sys
        import ahkpy as ahk
        ahk.hotkey("F24", sys.exit)
        ctx = ahk.HotkeyContext(lambda: True)
        ctx.hotkey("F13", ahk.message_box, "Boop")
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)

    boop_windows = ahk.windows.filter(title="Python.ahk", text="Boop")

    # A context-specific hotkey without a general counterpart requires a higher
    # send level to be triggered?
    settings.send_level = 10

    ahk.send("{F13}")
    assert boop_windows.wait(timeout=1)

    ahk.send("{F24}")
