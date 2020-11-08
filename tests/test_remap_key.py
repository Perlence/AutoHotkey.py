import ahkpy as ahk


def test_remap_key(request, child_ahk):
    def hotkeys():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F14", lambda: ahk.message_box("F14 pressed"))
        ahk.hotkey("F15", lambda: ahk.message_box("F15 pressed"))
        print("ok00")

    child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    remap = ahk.remap_key("F13", "F14")
    request.addfinalizer(remap.disable)
    # Use SendEvent here because remapping uses wildcard hotkeys that install
    # keyboard hook and SendInput temporarily disables that hook.
    ahk.send_event("{F13}", level=10)
    win_f14 = ahk.windows.filter(title="Python.ahk", text="F14 pressed")
    assert win_f14.wait(timeout=1)

    ctx_remap = win_f14.active_window_context().remap_key("F13", "F15")
    request.addfinalizer(ctx_remap.disable)
    ahk.send_event("{F13}", level=10)
    win_f15 = ahk.windows.filter(title="Python.ahk", text="F15 pressed")
    assert win_f15.wait(timeout=1)

    assert win_f15.close_all(timeout=1)
    assert win_f14.close_all(timeout=1)

    remap_mouse = ahk.remap_key("LButton", "F14")
    request.addfinalizer(remap_mouse.disable)
    ahk.send_event("{LButton}", level=10)
    assert win_f14.wait(timeout=1)
    assert win_f14.close_all(timeout=1)

    ahk.send("{F24}", level=10)
