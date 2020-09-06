import time
from dataclasses import FrozenInstanceError
from functools import partial

import pytest

import ahkpy as ahk


class TestWindows:
    @pytest.fixture(scope="class")
    def msg_boxes(self, child_ahk):
        def windows():
            import ahkpy as ahk
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

        assert ahk.windows.get_active()

        child_ahk.popen_code(windows)
        msg_boxes = ahk.windows.filter(title="win", exe="AutoHotkey.exe")

        with ahk.local_settings() as settings:
            settings.win_delay = 0

            wait_result = msg_boxes.wait(timeout=1)
            assert wait_result is not None
            assert isinstance(wait_result, ahk.Window)
            yield msg_boxes

        ahk.send("{F24}")

    @pytest.fixture(scope="class")
    def win1(self, msg_boxes):
        win1 = msg_boxes.first(title="win1")
        assert win1
        assert win1.exists
        return win1

    @pytest.fixture(scope="class")
    def win2(self, msg_boxes):
        win2 = msg_boxes.first(title="win2")
        assert win2
        assert win2.exists
        return win2

    def test_repr(self, msg_boxes):
        assert (
            repr(ahk.windows) ==
            "Windows(hidden_windows=False, hidden_text=True, title_mode='startswith', text_mode='fast')"
        )

        msg_boxes = ahk.windows.filter(title="win", exe="AutoHotkey.exe")
        assert (
            repr(msg_boxes) ==
            "Windows(title='win', exe='AutoHotkey.exe', "
            "hidden_windows=False, hidden_text=True, title_mode='startswith', text_mode='fast')"
        )

    def test_wait(self, msg_boxes):
        assert msg_boxes.wait(title="win1", timeout=1).title == "win1"
        assert msg_boxes.wait(title="win2", timeout=1).title == "win2"

    def test_len(self, msg_boxes):
        assert len(msg_boxes) == 2

    def test_iter(self, msg_boxes):
        ahk_window_list = list(msg_boxes)
        assert ahk_window_list != []

        top = msg_boxes.first()
        assert ahk_window_list[0] == top

        assert ahk_window_list[-1] == msg_boxes.last()

        assert repr(top) == f"Window(id={top.id})"

    def test_filter(self, msg_boxes):
        assert len(msg_boxes.filter(title="win2")) == 1
        assert msg_boxes.filter(title="win2").first().title == "win2"

    def test_exclude(self, msg_boxes):
        assert len(msg_boxes.exclude(title="win2")) == 1
        assert msg_boxes.exclude(title="win2").first().title == "win1"

    def test_minmax_all(self, msg_boxes):
        assert all(mb.is_restored for mb in msg_boxes)
        msg_boxes.minimize_all()
        assert all(mb.is_minimized for mb in msg_boxes)
        msg_boxes.maximize_all()
        assert all(mb.is_maximized for mb in msg_boxes)
        msg_boxes.restore_all()
        assert all(mb.is_restored for mb in msg_boxes)

    def test_activate(self, msg_boxes, win1, win2):
        assert win1.activate(timeout=1)
        assert win2.is_active is False

    def test_top_bottom(self, msg_boxes, win1):
        assert len(msg_boxes) == 2

        win1.bring_to_top()
        assert msg_boxes.first() == win1

        win1.send_to_bottom()
        ahk.sleep(.1)
        assert msg_boxes.last() == win1

        win1.bring_to_top()
        assert msg_boxes.first() == win1

    def test_match_first(self, msg_boxes, win1, win2):
        msg_boxes.minimize()
        assert win1.is_minimized is True
        ahk.sleep(.1)

        assert msg_boxes.activate(timeout=1)
        assert win2.is_active is True
        win1.restore()

        msg_boxes.maximize()
        assert win1.is_maximized is True
        win1.restore()

        msg_boxes.hide()
        assert win1.is_visible is False
        win1.show()

        msg_boxes.pin_to_top()
        assert win1.always_on_top is True
        msg_boxes.unpin_from_top()
        assert win1.always_on_top is False
        msg_boxes.toggle_always_on_top()
        assert win1.always_on_top is True

        msg_boxes.disable()
        assert win1.is_enabled is False

        msg_boxes.enable()
        assert win1.is_enabled is True

    def test_close(self, msg_boxes, win1):
        win1.activate(timeout=1)
        msg_boxes.close()  # Close actually hides this AHK message box
        assert not win1.wait_close(timeout=0.1)
        assert win1.wait_hidden(timeout=1)

        assert msg_boxes.wait_close(timeout=0.1) is False
        msg_boxes.close_all()
        assert msg_boxes.wait_close() is True
        assert not msg_boxes.exist()


class TestWindowObj:
    @pytest.fixture(scope="class")
    def win1(self, child_ahk):
        def window():
            import ahkpy as ahk
            import sys

            ahk.hotkey("F24", sys.exit)
            ahk.message_box("win1", title="win1")

        child_ahk.popen_code(window)

        win1 = ahk.windows.wait(title="win1", exe="AutoHotkey.exe")
        assert win1

        with ahk.local_settings() as settings:
            settings.win_delay = 0
            yield win1

        ahk.send("{F24}")

    def test_properties(self, win1):
        assert hash(win1) == hash(ahk.Window(win1.id))
        with pytest.raises(FrozenInstanceError):
            win1.id = 0

    def test_rect(self, win1):
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

    def test_title(self, win1):
        assert win1.title == "win1"
        win1.title = "win111"
        assert win1.title == "win111"

    def test_pid(self, win1):
        assert win1.pid > 0

    def test_process_name(self, win1):
        assert win1.process_name == "AutoHotkey.exe"

    def test_process_path(self, win1):
        assert win1.process_path.endswith(win1.process_name)

    def test_opacity(self, win1):
        assert win1.opacity is None
        win1.opacity = 128
        assert win1.opacity == 128
        win1.opacity = None
        assert win1.opacity is None

    def test_transparent_color(self, win1):
        assert win1.transparent_color is None
        win1.transparent_color = (255, 255, 255)
        assert win1.transparent_color == (255, 255, 255)
        win1.transparent_color = None
        assert win1.transparent_color is None

    def test_is_visible(self, win1):
        assert win1.is_visible is True
        win1.hide()
        assert win1.is_visible is False
        win1.show()
        assert win1.is_visible is True

    def test_minmax(self, win1):
        win1.maximize()
        assert win1.is_maximized is True
        win1.restore()
        assert win1.is_restored is True
        win1.minimize()
        assert win1.is_minimized is True
        win1.toggle_minimized()
        assert win1.is_restored is True
        assert win1.wait_active() is True
        assert win1.wait_close(timeout=0.1) is False

    def test_is_enabled(self, win1):
        assert win1.is_enabled is True
        win1.disable()
        assert win1.is_enabled is False
        win1.enable()
        assert win1.is_enabled is True
        win1.redraw()

    def test_always_on_top(self, win1):
        assert win1.always_on_top is False
        win1.toggle_always_on_top()
        assert win1.always_on_top is True
        win1.always_on_top = False
        assert win1.always_on_top is False
        win1.always_on_top = True
        assert win1.always_on_top is True
        win1.unpin_from_top()
        assert win1.always_on_top is False

    def test_get_status_bar_text(self, win1):
        assert win1.get_status_bar_text() is None

    def test_controls(self, win1):
        assert win1.control_classes == ["Button1", "Static1"]
        assert win1.controls == list(map(win1.get_control, win1.control_classes))

    def test_get_control(self, win1):
        assert win1.get_control("nooooooooooo") == ahk.Control(0)

        ok_btn = win1.get_control("Button1")
        assert ok_btn
        assert win1.get_control("OK") == ok_btn
        assert win1.get_control("K", match="contains") == ok_btn
        assert win1.get_control("^OK$", match="regex") == ok_btn

    def test_style(self, win1):
        assert isinstance(win1.style, ahk.WindowStyle)
        assert ahk.WindowStyle.POPUPWINDOW in win1.style
        assert ahk.WindowStyle.BORDER in win1.style
        win1.style ^= ahk.WindowStyle.BORDER
        assert ahk.WindowStyle.BORDER not in win1.style
        win1.redraw()

        assert isinstance(win1.ex_style, ahk.ExWindowStyle)
        assert win1.ex_style > 0


@pytest.mark.parametrize("win_id", [
    pytest.param(0, id="null window"),
    pytest.param(-1, id="nonexistent window"),
])
def test_nonwindow(win_id):
    win = ahk.Window(win_id)
    assert win.id == win_id
    assert win.exists is False
    assert win.is_active is False
    assert win.is_visible is False
    # assert win.hide() is None  # TODO: Don't raise errors
    # assert win.show() is None
    assert win.process_path is None
    assert win.title is None
    win.title = "beep"
    assert win.title is None
    assert win.class_name is None
    assert win.pid is None
    assert win.process_name is None
    assert win.x is None
    win.x = 99
    assert win.x is None
    assert win.width is None
    assert win.is_minimized is None
    assert win.is_maximized is None
    assert win.is_restored is None
    assert win.text is None
    assert win.control_classes == []
    assert win.controls == []
    assert win.get_control("nope") == ahk.Control(0)
    assert win.get_focused_control() == ahk.Control(0)
    assert win.always_on_top is None
    assert win.is_enabled is None  # XXX: Should it be False?
    # assert win.enable() is None
    # assert win.disable() is None
    assert win.style is None
    # win.style = 0
    # assert win.style is None
    assert win.ex_style is None
    # win.ex_style = 0
    # assert win.ex_style is None
    assert win.opacity is None
    assert win.transparent_color is None
    assert win.get_status_bar_text() is None
    assert win.wait_status_bar("sus") is None
    assert win.wait_active(timeout=0.1) is False
    assert win.wait_inactive(timeout=0.1) is True
    assert win.wait_hidden(timeout=0.1) is True
    assert win.wait_close(timeout=0.1) is True
    assert len(ahk.windows.filter(title=win.title)) == 0
    win.activate()


def test_status_bar(request, notepad):
    ahk.sleep(0.2)
    assert "Ln 1, Col 1" in notepad.get_status_bar_text(2)

    notepad.send("q")
    ahk.sleep(0)
    assert "Ln 1, Col 2" in notepad.get_status_bar_text(2)

    ahk.set_timer(partial(notepad.send, "q"), countdown=0.5)
    assert notepad.wait_status_bar("  Ln 1, Col x", part=2, timeout=0.1) is False
    assert notepad.wait_status_bar("  Ln 1, Col 3", part=2, timeout=1) is True
    assert notepad.get_status_bar_text(2) == "  Ln 1, Col 3"


def test_hidden_text():
    msg = "Type here to search"
    bar = ahk.windows.first(class_name="Shell_TrayWnd")
    assert bar
    assert msg in bar.text

    bar = ahk.windows.first(class_name="Shell_TrayWnd", text=msg)
    assert bar

    bar = ahk.windows.exclude_hidden_text().first(class_name="Shell_TrayWnd", text=msg)
    assert not bar


def test_title_match_mode(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.message_box("Hello", title="AutoHotkey")

    child_ahk.popen_code(code)
    settings.win_delay = 0

    ahk_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Hello")

    assert ahk_windows.wait(timeout=1)

    assert ahk_windows.exist(title="AutoHot")
    assert ahk_windows.exist(title="AutoHot", match="startswith")
    assert not ahk_windows.exist(title="utoHot", match="startswith")

    assert ahk_windows.exist(title="AutoHot", match="contains")
    assert ahk_windows.exist(title="toHot", match="contains")

    assert ahk_windows.exist(title="AutoHotkey", match="exact")
    assert not ahk_windows.exist(title="AutoHot", match="exact")
    assert not ahk_windows.exist(title="toHot", match="exact")

    assert ahk_windows.exist(title=r"Hotkey$", match="regex")
    assert ahk_windows.exist(exe=r"utoHotkey\.exe", match="regex")

    with pytest.raises(ValueError, match="is not a valid title match mode"):
        assert ahk_windows.exist(title="AutoHot", match="nooo")

    ahk.send("{F24}")


def test_match_text_slow(notepad):
    text = "beep boop autohotkey"
    notepad.send("{Text}" + text)
    ahk.sleep(0.1)
    assert text in notepad.text

    text_filter = ahk.windows.filter(exe="Notepad.exe", text=text)
    assert not text_filter.exist()
    assert text_filter.match_text_slow().exist()

    ahk.send("{F24}")


class TestControl:
    @pytest.fixture(autouse=True)
    def setup_clear_edit(self, notepad):
        edit = notepad.get_control("Edit1")
        edit.text = ""

    @pytest.fixture
    def find_dialog(self, notepad, setup_clear_edit):
        notepad.send("q")  # Enter some text to enable searching
        notepad.send("^f")
        find_dialog = ahk.windows.wait_active(title="Find", pid=notepad.pid, timeout=1)
        assert find_dialog
        yield find_dialog
        find_dialog.close()
        notepad.get_control("Edit1").text = ""

    @pytest.mark.parametrize("control_id", [
        pytest.param(0, id="null control"),
        pytest.param(-1, id="nonexistent control"),
    ])
    def test_noncontrol(self, control_id):
        ctl = ahk.Control(control_id)

        assert ctl.x is None
        ctl.x = 99
        assert ctl.x is None

        assert ctl.is_checked is None
        assert ctl.check() is None
        assert ctl.uncheck() is None

        assert ctl.is_enabled is None
        assert ctl.enable() is None
        assert ctl.disable() is None

        assert ctl.is_visible is False
        assert ctl.show() is None
        assert ctl.hide() is None

        assert ctl.is_focused is False
        assert ctl.focus() is None

        assert ctl.send("^r") is None
        assert ctl.send_message(9000) is None
        assert ctl.post_message(9000) is None

        assert ctl.text is None
        ctl.text = "nooooo"
        assert ctl.text is None

    def test_rect(self, notepad):
        edit = notepad.get_control("Edit1")
        _, _, width, height = edit.x, edit.y, edit.width, edit.height
        assert 0 < width <= notepad.width
        assert 0 < height <= notepad.height
        edit.width /= 2
        edit.height /= 2
        notepad.redraw()

    def test_checked(self, find_dialog):
        match_case_button = find_dialog.get_control("Button2")
        assert match_case_button.is_checked is False
        match_case_button.is_checked = True
        ahk.sleep(0)
        assert match_case_button.is_checked is True

        # find_next_button = find_dialog.get_control("Button7")
        # assert find_next_button.is_checked is False
        # find_next_button.is_checked = True
        # assert find_next_button.is_checked is False

    def test_is_enabled(self, notepad):
        edit = notepad.get_control("Edit1")
        assert edit.is_enabled is True
        edit.disable()
        assert edit.is_enabled is False
        edit.enable()
        assert edit.is_enabled is True

    def test_is_visible(self, notepad):
        edit = notepad.get_control("Edit1")
        assert edit.is_visible is True
        edit.hide()
        assert edit.is_visible is False
        edit.show()
        assert edit.is_visible is True

    def test_style(self, notepad):
        edit = notepad.get_control("Edit1")
        assert ahk.WindowStyle.VSCROLL in edit.style
        edit.style ^= ahk.WindowStyle.VSCROLL
        assert ahk.WindowStyle.VSCROLL not in edit.style
        notepad.redraw()

    def test_ex_style(self, notepad):
        edit = notepad.get_control("Edit1")
        assert edit.ex_style == 0
        edit.ex_style |= ahk.ExWindowStyle.LEFTSCROLLBAR
        assert ahk.ExWindowStyle.LEFTSCROLLBAR in edit.ex_style
        notepad.redraw()

    def test_focus(self, find_dialog):
        edit = find_dialog.get_control("Edit1")
        focused_control = find_dialog.get_focused_control()
        assert focused_control == edit
        assert focused_control.class_name == "Edit"
        assert focused_control.is_focused is True

        match_case_button = find_dialog.get_control("Button2")
        match_case_button.focus()
        focused_control = find_dialog.get_focused_control()
        assert focused_control == match_case_button
        assert match_case_button.is_focused is True
        assert edit.is_focused is False


def test_window_context(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", lambda: ahk.message_box("General"))
        ctx = ahk.windows.window_context(exe="AutoHotkey.exe", text="General")
        ctx.hotkey("F13", lambda: ahk.message_box("Context-specific"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="General")
    context_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Context-specific")

    assert not general_windows.exist()
    ahk.send("{F13}")
    assert general_windows.wait(timeout=1)
    assert not context_windows.exist()

    assert general_windows.exist()
    ahk.send("{F13}")
    assert context_windows.wait(timeout=1)

    ahk.send("{F24}")


def test_active_window_context(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", lambda: ahk.message_box("General"), max_threads=2)
        ctx = ahk.windows.active_window_context(exe="AutoHotkey.exe", text="General")
        ctx.hotkey("F13", lambda: ahk.message_box("Context-specific"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="General")
    context_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Context-specific")

    assert not general_windows.exist()
    ahk.send("{F13}")
    assert general_windows.wait(timeout=1)
    assert not context_windows.exist()

    assert general_windows.get_active()
    ahk.send("{F13}")
    assert context_windows.wait(timeout=1)
    assert len(general_windows) == 1

    assert general_windows.exist()
    assert not general_windows.get_active()
    ahk.send("{F13}")
    assert_equals_eventually(general_windows.__len__, 2)

    ahk.send("{F24}")


def test_exclude_window_context(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", lambda: ahk.message_box("General"), max_threads=2)
        ahk.hotkey("F14", lambda: ahk.message_box("Extra"))
        ctx = ahk.windows.filter(exe="AutoHotkey.exe").exclude(text="General").window_context()
        # If there are any AutoHotkey windows beside General.
        ctx.hotkey("F13", lambda: ahk.message_box("Context-specific"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="General")
    non_general_windows = ahk.windows.filter(exe="AutoHotkey.exe").exclude(text="General")
    extra_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Extra")
    context_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Context-specific")

    assert not non_general_windows.exist()
    ahk.send("{F13}")
    assert general_windows.wait(timeout=1)
    assert not context_windows.exist()

    ahk.send("{F14}")
    assert extra_windows.wait(timeout=1)

    assert non_general_windows.exist()
    ahk.send("{F13}")
    assert context_windows.wait(timeout=1)

    ahk.send("{F24}")


def test_exclude_active_window_context(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", lambda: ahk.message_box("General"), max_threads=3)
        ahk.hotkey("F14", lambda: ahk.message_box("Extra"))
        ctx = ahk.windows.filter(exe="AutoHotkey.exe").exclude(text="General").active_window_context()
        # If there are any active AutoHotkey windows beside General.
        ctx.hotkey("F13", lambda: ahk.message_box("Context-specific"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="General")
    non_general_windows = ahk.windows.filter(exe="AutoHotkey.exe").exclude(text="General")
    extra_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Extra")
    context_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Context-specific")

    assert not non_general_windows.exist()
    ahk.send("{F13}")
    assert general_windows.wait(timeout=1)
    assert not context_windows.exist()

    ahk.send("{F14}")
    assert extra_windows.wait(timeout=1)

    assert non_general_windows.get_active()
    ahk.send("{F13}")
    assert context_windows.wait(timeout=1)

    assert context_windows.close_all(timeout=1)
    assert general_windows.activate(timeout=1)
    assert non_general_windows.exist()
    assert not non_general_windows.get_active()
    ahk.send("{F13}")
    assert_equals_eventually(general_windows.__len__, 2)

    ahk.send("{F24}")


def assert_equals_eventually(func, expected, timeout=1):
    stop = time.perf_counter() + timeout
    while time.perf_counter() < stop:
        actual = func()
        if actual == expected:
            return
        ahk.sleep(0.01)
    assert actual == expected


def test_include_hidden_context(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ctx = ahk.windows.window_context(exe="AutoHotkey.exe")
        ctx.hotkey("F13", lambda: ahk.message_box("Context-specific"))
        ahk.Window(-1).exists  # This sets DetectHiddenWindows, On
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    ahk_windows = ahk.windows.filter(exe="AutoHotkey.exe")
    context_windows = ahk_windows.filter(text="Context-specific")

    assert not ahk_windows.exist()
    assert ahk_windows.include_hidden_windows().exist()
    # XXX: Why doesn't child AHK recognize F13 unless the level is set?
    ahk.send("{F13}", level=10)
    assert not context_windows.wait(timeout=0.1)

    ahk.send("{F24}")


# TODO: Write nonexistent/inactive window context tests.
