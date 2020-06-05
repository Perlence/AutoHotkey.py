import ahk


def test_windows(child_ahk):
    def windows():
        import ahk
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.set_timer(countdown=0.1)
        def win1():
            ahk.message_box("win1", title="win1")

        @ahk.set_timer(countdown=0.2)
        def win2():
            ahk.message_box("win2", title="win2")

    child_ahk.popen_code(windows)

    assert repr(ahk.windows) == "Windows()"
    ahk_windows = ahk.windows.filter(exe="AutoHotkey.exe")
    assert repr(ahk_windows) == "Windows(exe='AutoHotkey.exe')"
    assert ahk_windows.wait(1) is True
    assert len(ahk_windows) == 2
    ahk_window_list = list(ahk_windows)
    assert ahk_window_list != []
    top = ahk_windows.first()
    assert ahk_window_list[0] == top
    assert ahk_window_list[-1] == ahk_windows.last()
    assert repr(top) == f"Window(id={top.id})"

    assert len(ahk_windows.filter(title="win2")) == 1
    assert ahk_windows.filter(title="win2").first().title == "win2"
    assert len(ahk_windows.exclude(title="win2")) == 1
    assert ahk_windows.exclude(title="win2").first().title == "win1"

    ahk.send("{F24}")
