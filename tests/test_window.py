import subprocess

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

        ahk.sleep(1)
        sys.exit()

    child_ahk.popen_code(windows)
    ahk.set_win_delay(None)

    assert repr(ahk.windows) == "Windows()"

    msg_boxes = ahk.windows.filter(exe="AutoHotkey.exe")
    assert repr(msg_boxes) == "Windows(exe='AutoHotkey.exe')"

    wait_result = msg_boxes.wait(timeout=1)
    assert wait_result is not None
    assert isinstance(wait_result, ahk.Window)
    assert msg_boxes.wait(title="win1", timeout=1).title == "win1"
    assert msg_boxes.wait(title="win2", timeout=1).title == "win2"

    assert len(msg_boxes) == 2
    ahk_window_list = list(msg_boxes)
    assert ahk_window_list != []
    top = msg_boxes.first()
    assert ahk_window_list[0] == top
    assert ahk_window_list[-1] == msg_boxes.last()
    assert repr(top) == f"Window(id={top.id})"

    assert len(msg_boxes.filter(title="win2")) == 1
    assert msg_boxes.filter(title="win2").first().title == "win2"
    assert len(msg_boxes.exclude(title="win2")) == 1
    assert msg_boxes.exclude(title="win2").first().title == "win1"

    assert all(not mb.minimized and not mb.maximized for mb in msg_boxes)
    msg_boxes.minimize_all()
    assert all(mb.minimized for mb in msg_boxes)
    msg_boxes.maximize_all()
    assert all(mb.maximized for mb in msg_boxes)
    msg_boxes.restore_all()
    assert all(not mb.minimized and not mb.maximized for mb in msg_boxes)

    # Individual window
    win1 = msg_boxes.first(title="win1")
    assert win1
    assert win1.exists

    win2 = msg_boxes.first(title="win2")
    win1.activate()
    assert not win2.active

    _, _, width, height = win1.rect
    x, y = win1.position
    win1.y += 100
    assert win1.y == y + 100
    win1.x = win1.y
    assert win1.x == win1.y
    win1.height += 100
    assert win1.height == height + 100
    win1.height = win1.width
    assert win1.height == win1.width

    assert win1.title == "win1"
    win1.title = "win111"
    assert win1.title == "win111"

    assert win1.pid > 0

    assert ahk.windows.first(class_name="totally no such window").transparent is None
    assert win1.transparent is None
    win1.transparent = 128
    assert win1.transparent == 128
    win1.transparent = None
    assert win1.transparent is None

    assert win1.transparent_color is None
    win1.transparent_color = (255, 255, 255)
    assert win1.transparent_color == (255, 255, 255)
    win1.transparent_color = None
    assert win1.transparent_color is None

    win1.hide()
    win1.show()
    win1.maximize()
    assert win1.maximized
    win1.restore()
    assert win1.restored
    win1.minimize()
    assert win1.minimized
    win1.restore()
    assert win1.restored
    assert win1.wait_active() is True
    assert win1.wait_close(timeout=0.1) is False

    assert msg_boxes.wait_close(timeout=0.1) is False
    msg_boxes.close_all()
    assert msg_boxes.wait_close() is True
    assert not msg_boxes.first()

    ahk.send("{F24}")


def test_status_bar():
    notepad_proc = subprocess.Popen(["notepad.exe"])
    notepad_win = ahk.windows.wait(pid=notepad_proc.pid)
    assert notepad_win
    assert "Ln 1, Col 1" in notepad_win.get_status_bar_text(2)
    notepad_win.send("q")
    assert "Ln 1, Col 2" in notepad_win.get_status_bar_text(2)
    notepad_proc.terminate()
