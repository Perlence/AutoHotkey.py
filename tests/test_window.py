import dataclasses
import subprocess
import uuid

import pytest

import ahkpy as ahk
from .conftest import assert_equals_eventually


class TestWindows:
    @pytest.fixture(scope="class")
    def msg_boxes(self, child_ahk):
        def windows():
            import ahkpy as ahk
            import sys

            ahk.hotkey("F24", sys.exit)

            ahk.set_countdown(0.1, ahk.message_box, "win1", "ahkpy win1")
            ahk.set_countdown(0.3, ahk.message_box, "win2", "ahkpy win2")
            ahk.sleep(1)
            sys.exit()

        assert ahk.windows.wait_active()

        child_ahk.popen_code(windows)
        msg_boxes = ahk.windows.filter(title="ahkpy win")

        with ahk.local_settings() as settings:
            settings.win_delay = 0

            wait_result = msg_boxes.wait(timeout=1)
            assert wait_result is not None
            assert isinstance(wait_result, ahk.Window)
            yield msg_boxes

        ahk.send("{F24}")

    @pytest.fixture(scope="class")
    def win1(self, msg_boxes):
        win1 = msg_boxes.first(title="ahkpy win1")
        assert win1
        assert win1.exists
        return win1

    @pytest.fixture(scope="class")
    def win2(self, msg_boxes):
        win2 = msg_boxes.first(title="ahkpy win2")
        assert win2
        assert win2.exists
        return win2

    def test_repr(self, msg_boxes):
        assert (
            repr(ahk.windows) ==
            "Windows(hidden_windows=False, hidden_text=True, title_mode='startswith', text_mode='fast')"
        )

        msg_boxes = ahk.windows.filter(title="ahkpy win")
        assert (
            repr(msg_boxes) ==
            "Windows(title='ahkpy win', "
            "hidden_windows=False, hidden_text=True, title_mode='startswith', text_mode='fast')"
        )

    def test_wait(self, msg_boxes):
        assert msg_boxes.wait(title="ahkpy win1", timeout=1).title == "ahkpy win1"
        assert msg_boxes.wait(title="ahkpy win2", timeout=1).title == "ahkpy win2"

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
        assert len(msg_boxes.filter(title="ahkpy win2")) == 1
        assert msg_boxes.filter(title="ahkpy win2").first().title == "ahkpy win2"

    def test_exclude(self, msg_boxes):
        assert len(msg_boxes.exclude(title="ahkpy win2")) == 1
        assert msg_boxes.exclude(title="ahkpy win2").first().title == "ahkpy win1"

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
        assert msg_boxes.wait_inactive(id=win2.id, timeout=1)
        assert win2.wait_inactive(timeout=1)
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

    def test_wait_close_none(self):
        assert ahk.windows.filter(title=None).wait_close() is True

    def test_close(self, msg_boxes, win1):
        win1.activate(timeout=1)
        assert msg_boxes.first().close() is False  # Close actually hides this AHK message box
        assert not win1.wait_close(timeout=0.1)
        assert win1.wait_hidden(timeout=1)

        assert msg_boxes.wait_close(timeout=0.1) is False
        assert msg_boxes.close_all() is True
        assert msg_boxes.wait_close() is True
        assert not msg_boxes.exist()


class TestWindowObj:
    @pytest.fixture(scope="class")
    def win1(self, child_ahk):
        def window():
            import ahkpy as ahk
            import sys

            ahk.hotkey("F24", sys.exit)
            ahk.message_box("win1", title="ahkpy win1")

        child_ahk.popen_code(window)

        win1 = ahk.windows.wait(title="ahkpy win1")
        assert win1

        with ahk.local_settings() as settings:
            settings.win_delay = 0
            yield win1

        ahk.send("{F24}")

    def test_properties(self, win1):
        assert hash(win1) == hash(ahk.Window(win1.id))
        with pytest.raises(dataclasses.FrozenInstanceError):
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
        assert win1.title == "ahkpy win1"
        win1.title = "ahkpy win111"
        assert win1.title == "ahkpy win111"

        win1.title = "123"
        assert win1.title == "123"

    def test_pid(self, win1):
        assert win1.pid > 0

    def test_process_name(self, win1):
        assert win1.process_name.startswith("AutoHotkey")
        assert win1.process_name.endswith(".exe")

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
        assert win1.get_control("nooooooooooo") == ahk.Control(None)

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


def test_nonexistent_window():
    win = ahk.Window(None)
    assert win.exists is False
    assert win.is_active is False
    assert win.is_visible is False
    assert win.hide() is None
    assert win.show() is None
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
    assert win.control_classes is None
    assert win.controls is None
    assert win.get_control("nope") == ahk.Control(None)
    assert win.get_focused_control() == ahk.Control(None)
    assert win.always_on_top is None
    assert win.is_enabled is None  # TODO: Should it be False?
    assert win.enable() is None
    assert win.disable() is None
    assert win.style is None
    win.style = 0
    assert win.style is None
    assert win.ex_style is None
    win.ex_style = 0
    assert win.ex_style is None
    assert win.opacity is None
    assert win.transparent_color is None
    assert win.get_status_bar_text() is None
    assert win.wait_status_bar("sus") is None
    assert win.wait_active(timeout=0.1) is False
    assert win.wait_inactive(timeout=0.1) is True
    assert win.wait_hidden(timeout=0.1) is True
    assert win.wait_close(timeout=0.1) is True
    assert len(ahk.windows.filter(title=win.title)) == 0
    assert win.activate() is False
    assert win.send("^r") is None
    assert win.send_message(9000) is None
    assert win.post_message(9000) is None


def test_status_bar(notepad):
    ahk.sleep(0.2)
    assert "Ln 1, Col 1" in notepad.get_status_bar_text(1)

    notepad.send("q")
    ahk.sleep(0)
    assert "Ln 1, Col 2" in notepad.get_status_bar_text(1)

    ahk.set_countdown(0.5, notepad.send, "q")
    assert notepad.wait_status_bar("  Ln 1, Col x", part=1, timeout=0.1) is False
    assert notepad.wait_status_bar("  Ln 1, Col 3", part=1, timeout=1) is True
    assert notepad.get_status_bar_text(1) == "  Ln 1, Col 3"


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
        ahk.message_box("Hello from AutoHotkey.py", title="AutoHotkey")

    child_ahk.popen_code(code)
    settings.win_delay = 0

    ahk_windows = ahk.windows.filter(text="Hello from AutoHotkey.py")

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
    assert ahk_windows.exist(exe=r"utoHotkey.*\.exe", match="regex")

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
    @pytest.fixture
    def edit(self, notepad):
        edit = notepad.get_control("Edit1")
        assert edit
        edit.text = ""
        return edit

    @pytest.fixture
    def find_dialog(self, notepad, edit):
        edit.text = "q"  # Enter some text to enable searching
        assert ahk.windows.get_active().id == notepad.id
        ahk.send("^f")
        find_dialog = ahk.windows.wait_active(title="Find", pid=notepad.pid, timeout=1)
        assert find_dialog
        yield find_dialog
        assert find_dialog.close(timeout=1)
        notepad.get_control("Edit1").text = ""

    def test_nonexistent_control(self):
        ctl = ahk.Control(None)

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

        assert ctl.line_count is None
        assert ctl.current_line_number is None
        assert ctl.current_column is None
        assert ctl.get_line(1) is None
        assert ctl.current_line is None
        assert ctl.selected_text is None
        assert ctl.paste("beep") is None

        assert ctl.list_choice is None
        assert ctl.list_choice_index is None
        assert ctl.choose_item("huh") is None
        assert ctl.choose_item_index(4) is None
        assert ctl.list_item_index("huh") is None
        assert ctl.list_items is None
        assert ctl.selected_list_items is None
        assert ctl.focused_list_item is None
        assert ctl.get_list_items(column=0) is None
        assert ctl.list_item_count is None
        assert ctl.selected_list_item_count is None
        assert ctl.focused_list_item_index is None
        assert ctl.list_view_column_count is None

    def test_rect(self, notepad, edit):
        _, _, width, height = edit.x, edit.y, edit.width, edit.height
        assert 0 < width <= notepad.width
        assert 0 < height <= notepad.height
        edit.width /= 2
        edit.height /= 2
        notepad.redraw()

    def test_checked(self, request, find_dialog):
        match_case_button = find_dialog.get_control("Button2")
        initial = match_case_button.is_checked
        match_case_button.is_checked = not initial
        request.addfinalizer(lambda: setattr(match_case_button, "is_checked", initial))
        assert_equals_eventually(lambda: match_case_button.is_checked, not initial)
        match_case_button.is_checked = initial
        assert_equals_eventually(lambda: match_case_button.is_checked, initial)

        # find_next_button = find_dialog.get_control("Button7")
        # assert find_next_button.is_checked is False
        # find_next_button.is_checked = True
        # assert find_next_button.is_checked is False

    def test_is_enabled(self, edit):
        assert edit.is_enabled is True
        edit.disable()
        assert edit.is_enabled is False
        edit.enable()
        assert edit.is_enabled is True

    def test_is_visible(self, edit):
        assert edit.is_visible is True
        edit.hide()
        assert edit.is_visible is False
        edit.show()
        assert edit.is_visible is True

    def test_style(self, notepad, edit):
        assert ahk.WindowStyle.VSCROLL in edit.style
        edit.style ^= ahk.WindowStyle.VSCROLL
        assert ahk.WindowStyle.VSCROLL not in edit.style
        notepad.redraw()

    def test_ex_style(self, notepad, edit):
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
        assert_equals_eventually(
            lambda: (match_case_button.focus(), find_dialog.get_focused_control())[1],
            match_case_button,
        )
        assert match_case_button.is_focused is True
        assert edit.is_focused is False

    def test_text(self, edit):
        edit.text = "123"
        assert edit.text == "123"

    def test_paste(self, edit):
        text = str(uuid.uuid4())
        edit.paste(text)
        assert edit.text == text

        cb = ahk.get_clipboard()
        assert cb != text

    def test_line_stuff(self, notepad, edit: ahk.Control):
        edit.text = ""
        assert edit.line_count == 1

        edit.text = "0\r\n1"
        assert edit.line_count == 2

        edit.text = "0\r\n1\r\n"
        assert edit.line_count == 3

        assert edit.current_line_number == 0
        assert edit.current_column == 0

        edit.send("{Right}")
        assert edit.current_column == 1

        assert edit.current_line == "0"

        edit.send("{Down}")
        assert edit.current_line_number == 1
        assert edit.current_line == "1"
        assert edit.current_column == 1

        edit.send("{Left}")
        assert edit.current_column == 0

        assert edit.get_line(0) == "0"
        assert edit.get_line(1) == "1"
        assert edit.get_line(2) == ""
        assert edit.get_line(-1) == ""
        assert edit.get_line(-2) == "1"
        assert edit.get_line(-3) == "0"
        with pytest.raises(ahk.Error, match="line number out of range"):
            assert edit.get_line(3)
        with pytest.raises(ahk.Error, match="line number out of range"):
            assert edit.get_line(4)
        with pytest.raises(ahk.Error, match="line number out of range"):
            assert edit.get_line(-5)

        assert edit.selected_text == ""

        assert ahk.windows.get_active().id == notepad.id
        ahk.send("+{Right}")
        assert edit.selected_text == "1"

        ahk.send("^a")
        assert_equals_eventually(lambda: edit.selected_text, "0\r\n1\r\n")

    @pytest.fixture(scope="class")
    def list_playground(self, request):
        proc = subprocess.Popen([ahk.executable, "/CP65001", "*"], stdin=subprocess.PIPE, encoding='utf-8')
        request.addfinalizer(proc.terminate)
        proc.stdin.write("""\
            Gui, Add, ComboBox, vColorChoice, Red|Green|Синий|Black|White

            Gui, Add, ListBox, r5 vColorChoiceList, Red|Green|Синий|Black|White

            Gui, Add, ListView,, Col1|Col2
            LV_Add("", "Hello", "0")
            LV_Add("", "Hello wow", "1")
            LV_Add("", "Hello world", "2")
            LV_ModifyCol()

            Gui, Show
            return

            GuiClose:
                ExitApp
        """)
        proc.stdin.close()

        win = ahk.windows.wait(pid=proc.pid)
        assert win

        yield win

        win.close(timeout=1)

    @pytest.fixture
    def list_view(self, list_playground):
        list_view = list_playground.get_control("SysListView321")
        assert list_view
        return list_view

    @pytest.fixture
    def combobox(self, list_playground):
        combobox = list_playground.get_control("ComboBox1")
        assert combobox
        return combobox

    @pytest.fixture
    def listbox(self, list_playground):
        listbox = list_playground.get_control("ListBox1")
        assert listbox
        return listbox

    @pytest.fixture(params=["combobox", "listbox"])
    def list_ctl(self, request):
        return request.getfixturevalue(request.param)

    def test_list_items(self, request, list_ctl):
        assert list_ctl.list_items == ["Red", "Green", "Синий", "Black", "White"]
        assert list_ctl.list_choice_index == -1
        assert list_ctl.list_choice is None

        list_ctl.send("{Down}")
        assert list_ctl.list_choice_index == 0
        assert list_ctl.list_choice == "Red"

        assert list_ctl.list_item_index("Синий") == 2
        assert list_ctl.list_item_index("Nooo") == -1

        list_ctl.choose_item("Black")
        assert list_ctl.list_choice_index == 3

        with pytest.raises(ahk.Error, match="doesn't exist"):
            list_ctl.choose_item("Nooo")
        assert list_ctl.list_choice_index == 3

        list_ctl.choose_item_index(0)
        assert list_ctl.list_choice_index == 0

        list_ctl.choose_item_index(-2)
        assert list_ctl.list_choice_index == 3

    def test_list_view_items(self, list_view: ahk.Control):
        assert list_view.list_items == [["Hello", "0"], ["Hello wow", "1"], ["Hello world", "2"]]
        assert list_view.selected_list_items == []
        assert list_view.focused_list_item is None
        assert list_view.list_item_count == 3
        assert list_view.selected_list_item_count == 0
        assert list_view.focused_list_item_index == -1
        assert list_view.list_view_column_count == 2
        assert list_view.get_list_items(column=0) == ["Hello", "Hello wow", "Hello world"]
        assert list_view.get_list_items(column=-1) == ["0", "1", "2"]
        with pytest.raises(ahk.Error, match="column index out of range"):
            assert list_view.get_list_items(column=99)
        assert list_view.get_list_items(selected=True, focused=True) == []

        list_view.focus()
        list_view.send("+{Down 2}")
        assert list_view.selected_list_items == [["Hello", "0"], ["Hello wow", "1"]]
        assert list_view.focused_list_item == ["Hello wow", "1"]
        assert list_view.selected_list_item_count == 2
        assert list_view.focused_list_item_index == 1
        assert list_view.get_list_items(selected=True, focused=True) == [["Hello wow", "1"]]


def test_window_context(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", ahk.message_box, "General")
        ctx = ahk.windows.window_context(title="Python.ahk", text="General")
        ctx.hotkey("F13", ahk.message_box, "Context-specific")
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(title="Python.ahk", text="General")
    context_windows = ahk.windows.filter(title="Python.ahk", text="Context-specific")

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
        ahk.hotkey("F13", ahk.message_box, "General", max_threads=2)
        ctx = ahk.windows.active_window_context(title="Python.ahk", text="General")
        ctx.hotkey("F13", ahk.message_box, "Context-specific")
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(title="Python.ahk", text="General")
    context_windows = ahk.windows.filter(title="Python.ahk", text="Context-specific")

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
        ahk.hotkey("F13", ahk.message_box, "General", max_threads=2)
        ahk.hotkey("F14", ahk.message_box, "Extra")
        ctx = ahk.windows.filter(title="Python.ahk").exclude(text="General").window_context()
        # If there are any AutoHotkey windows beside General.
        ctx.hotkey("F13", ahk.message_box, "Context-specific")
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(title="Python.ahk", text="General")
    non_general_windows = ahk.windows.filter(title="Python.ahk").exclude(text="General")
    extra_windows = ahk.windows.filter(title="Python.ahk", text="Extra")
    context_windows = ahk.windows.filter(title="Python.ahk", text="Context-specific")

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
        ahk.hotkey("F13", ahk.message_box, "General", max_threads=3)
        ahk.hotkey("F14", ahk.message_box, "Extra")
        ctx = ahk.windows.filter(title="Python.ahk").exclude(text="General").active_window_context()
        # If there are any active AutoHotkey windows beside General.
        ctx.hotkey("F13", ahk.message_box, "Context-specific")
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    general_windows = ahk.windows.filter(title="Python.ahk", text="General")
    non_general_windows = ahk.windows.filter(title="Python.ahk").exclude(text="General")
    extra_windows = ahk.windows.filter(title="Python.ahk", text="Extra")
    context_windows = ahk.windows.filter(title="Python.ahk", text="Context-specific")

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
    assert general_windows.first().activate(timeout=1)
    assert non_general_windows.exist()
    assert not non_general_windows.get_active()
    ahk.send("{F13}")
    assert_equals_eventually(general_windows.__len__, 2)

    ahk.send("{F24}")


def test_include_hidden_context(child_ahk, settings):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ctx = ahk.windows.window_context(title="Python.ahk - - ", match="contains")
        ctx.hotkey("F13", ahk.message_box, "Context-specific")
        ahk.Window(-1).exists  # This sets DetectHiddenWindows, On
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)
    settings.win_delay = 0

    ahk_windows = ahk.windows.filter(title="Python.ahk - - ", match="contains")
    context_windows = ahk_windows.filter(text="Context-specific")

    assert not ahk_windows.exist()
    assert ahk_windows.include_hidden_windows().exist()
    # TODO: Why doesn't child AHK recognize F13 unless the level is set?
    ahk.send("{F13}", level=10)
    assert not context_windows.wait(timeout=0.1)

    ahk.send("{F24}")


# TODO: Write nonexistent/inactive window context tests.
