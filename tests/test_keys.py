import subprocess
import sys
from textwrap import dedent

import pytest

import _ahk  # noqa
import ahkpy as ahk


def test_get_key_state(child_ahk):
    with pytest.raises(ValueError, match="key_name is invalid or the state of the key could not be determined"):
        ahk.get_key_state("beep")

    assert ahk.get_key_state("F13") is False
    ahk.send("{F13 Down}")
    assert ahk.get_key_state("F13") is True
    ahk.send("{F13 Up}")
    assert ahk.get_key_state("F13") is False


def test_is_key_toggled():
    with pytest.raises(ValueError, match="key_name must be one of"):
        ahk.is_key_toggled("F13")

    initial_state = ahk.is_key_toggled("CapsLock")
    assert isinstance(initial_state, bool)
    ahk.set_caps_lock_state(True)
    assert ahk.is_key_toggled("CapsLock") is True
    ahk.set_caps_lock_state(False)
    assert ahk.is_key_toggled("CapsLock") is False
    ahk.set_caps_lock_state(initial_state)


def test_hotkey_refcounts():
    func1 = lambda: None  # noqa
    func2 = lambda: None  # noqa
    func1_refcount = sys.getrefcount(func1)
    func2_refcount = sys.getrefcount(func2)

    hk = ahk.hotkey("F13", func1)
    assert hk.key_name == "F13"
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount

    hk.update(func=func2)
    assert sys.getrefcount(func1) == func1_refcount
    assert sys.getrefcount(func2) == func2_refcount + 1

    hk.update(func=func1)
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount

    hk.update(func=func1)
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount


class TestHotkey:
    def test_exceptions(self):
        with pytest.raises(ahk.Error, match="invalid key name"):
            ahk.hotkey("")

        with pytest.raises(TypeError, match="must be callable"):
            ahk.hotkey("^t", func="not callable")

    def test_hotkey_field(self):
        hk = ahk.hotkey("F13", lambda: None)
        assert hk.key_name == "F13"
        hk.disable()

    def test_hotkeys_in_child_ahk(self, child_ahk):
        def hotkeys():
            import ahkpy as ahk
            import sys

            ahk.hotkey("F24", sys.exit)

            @ahk.hotkey("F14")
            def show_msgbox():
                ahk.message_box("Hello from hotkey.")

            @ahk.hotkey("F15")
            def show_bang():
                1 / 0

            @ahk.hotkey("F16")
            def disable_ctrl_t():
                show_msgbox.disable()
                print("ok01")

            @ahk.hotkey("F17")
            def enable_ctrl_t():
                show_msgbox.enable()
                print("ok02")

            @ahk.hotkey("F18")
            def change_f14():
                show_msgbox.update(func=lambda: print("ok04"))
                print("ok03")

            print("ok00")

        proc = child_ahk.popen_code(hotkeys)
        child_ahk.wait(0)

        msg_boxes = ahk.windows.filter(title="Python.ahk")
        assert not msg_boxes.get_active(text="Hello from hotkey")
        ahk.send("{F14}")
        assert msg_boxes.wait(text="Hello from hotkey", timeout=0.5)
        msg_boxes.send("{Space}")

        assert not msg_boxes.get_active(text="ZeroDivisionError")
        ahk.send("{F15}")
        assert msg_boxes.wait(text="ZeroDivisionError", timeout=0.5)

        msg_boxes.send("{Space}")
        assert msg_boxes.wait_close(text="ZeroDivisionError", timeout=1)

        ahk.send("{F16}")  # Disable {F14}
        child_ahk.wait(1)
        ahk.send("{F14}")
        assert not msg_boxes.wait(text="Hello from hotkey", timeout=0.5)

        ahk.send("{F17}")  # Enable {F14}
        child_ahk.wait(2)
        ahk.send("{F14}")
        assert msg_boxes.wait(text="Hello from hotkey", timeout=1)

        msg_boxes.send("{Space}")
        assert msg_boxes.wait_close(text="Hello from hotkey", timeout=1)

        ahk.send("{F18}")  # Change the handler of {F14} to print "ok04"
        child_ahk.wait(3)
        ahk.send("{F14}")
        assert not msg_boxes.wait(text="Hello from hotkey", timeout=0.5)
        child_ahk.wait(4)

        ahk.send("{F24}")
        child_ahk.close()
        assert "ZeroDivisionError:" in proc.stderr.read()
        assert proc.returncode == 0


class TestHotstring:
    @pytest.fixture(scope="class")
    def notepad(self, request):
        notepad_proc = subprocess.Popen(["notepad.exe"])
        try:
            notepad_win = ahk.windows.wait(pid=notepad_proc.pid)
            yield notepad_win
        finally:
            notepad_proc.terminate()

    @pytest.fixture
    def edit(self, notepad):
        edit = notepad.get_control("Edit1")
        edit.text = ""
        assert edit.text == ""
        yield edit
        edit.text = ""
        assert edit.text == ""

    def test_simple(self, request, edit):
        dashes = ahk.hotstring("--", "—")
        request.addfinalizer(dashes.disable)
        ahk.send("--", level=10)
        ahk.sleep(0)
        assert edit.text == "--"
        ahk.send(" ", level=10)
        ahk.sleep(0)
        assert edit.text == "— "

    def test_wait_for_and_omit_end_char(self, request, edit):
        jsmith = ahk.hotstring("j@", "jsmith@somedomain.com", wait_for_end_char=False)
        request.addfinalizer(jsmith.disable)
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com"

        edit.text = ""
        jsmith.update(wait_for_end_char=False, omit_end_char=False)
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com"

        edit.text = ""
        jsmith.update(wait_for_end_char=False, omit_end_char=True)
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com"

        edit.text = ""
        jsmith.update(omit_end_char=False)  # wait_for_end_char=False implied
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com"

        edit.text = ""
        jsmith.update(omit_end_char=True)
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "j@"
        ahk.send(" ", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com"

        edit.text = ""
        jsmith.update(wait_for_end_char=True)  # omit_end_char implied
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "j@"
        ahk.send(" ", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com"

        edit.text = ""
        jsmith.update(wait_for_end_char=True, omit_end_char=False)
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "j@"
        ahk.send(" ", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com "

        edit.text = ""
        jsmith.update(wait_for_end_char=True, omit_end_char=True)
        ahk.send("j@", level=10)
        ahk.sleep(0)
        assert edit.text == "j@"
        ahk.send(" ", level=10)
        ahk.sleep(0)
        assert edit.text == "jsmith@somedomain.com"

        edit.text = ""
        dashes = ahk.hotstring("--", "—")
        request.addfinalizer(dashes.disable)
        dashes.update(wait_for_end_char=False)
        ahk.send("--", level=10)
        ahk.sleep(0)
        assert edit.text == "—"

        edit.text = ""
        dashes.update(wait_for_end_char=True)
        ahk.send("--", level=10)
        ahk.sleep(0)
        assert edit.text == "--"
        ahk.send(" ", level=10)
        ahk.sleep(0)
        assert edit.text == "— "

    def test_on_off(self, request, edit):
        beep = ahk.hotstring("beep", "boop")
        request.addfinalizer(beep.disable)
        ahk.send("Beep ", level=10)
        ahk.sleep(0)
        assert edit.text == "Boop "

        edit.text = ""
        beep.disable()
        ahk.send("Beep ", level=10)
        ahk.sleep(0)
        assert edit.text == "Beep "

        edit.text = ""
        beep.enable()
        ahk.send("Beep ", level=10)
        ahk.sleep(0)
        assert edit.text == "Boop "

        edit.text = ""
        beep.toggle()
        ahk.send("Beep ", level=10)
        ahk.sleep(0)
        assert edit.text == "Beep "

    def test_case_sensitive(self, request, edit):
        case = ahk.hotstring("CaSe", "EsAc", case_sensitive=True)
        request.addfinalizer(case.disable)
        ahk.send("case ", level=10)
        ahk.sleep(0)
        assert edit.text == "case "
        ahk.send("CaSe ", level=10)
        ahk.sleep(0)
        assert edit.text == "case EsAc "

    def test_decorator(self, request, edit):
        @ahk.hotstring("blarp")
        def blarp():
            ahk.send('boop ', level=10)

        request.addfinalizer(blarp.disable)
        ahk.send("blarp", level=10)
        ahk.sleep(0)
        assert edit.text == "blarp"
        ahk.send(" ", level=10)
        ahk.sleep(0)
        assert edit.text == "boop "

    def test_replace_inside_word(self, request, edit):
        airline = ahk.hotstring("al", "airline", replace_inside_word=True)
        request.addfinalizer(airline.disable)
        ahk.send("practical ", level=10)
        ahk.sleep(0)
        assert edit.text == "practicairline "

    def test_no_backspacing(self, request, edit):
        em = ahk.hotstring("<em>", "</em>{left 5}", wait_for_end_char=False, backspacing=False)
        request.addfinalizer(em.disable)
        ahk.send("hello <em>world", level=10)
        ahk.sleep(0)
        assert edit.text == "hello <em>world</em>"

    def test_conform_to_case(self, request, edit):
        pillow = ahk.hotstring("pillow", "wollip", conform_to_case=False)
        request.addfinalizer(pillow.disable)
        ahk.send("pillow ", level=10)
        ahk.sleep(0)
        assert edit.text == "wollip "

        edit.text = ""
        ahk.send("PILLOW ", level=10)
        ahk.sleep(0)
        assert edit.text == "wollip "

        edit.text = ""
        ahk.send("PiLLoW ", level=10)
        ahk.sleep(0)
        assert edit.text == "wollip "

    def test_active_window_context(self, request, edit):
        notepad_ctx = ahk.windows.active_window_context(class_name="Notepad")
        padnote = notepad_ctx.hotstring("notepad", "padnote")
        request.addfinalizer(padnote.disable)
        ahk.send("notepad ", level=10)
        ahk.sleep(0)
        assert edit.text == "padnote "


def test_hotkey_context(child_ahk):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", lambda: ahk.message_box("Beep"))
        ctx = ahk.HotkeyContext(lambda: ahk.windows.get_active(exe="AutoHotkey.exe", text="Beep"))
        ctx.hotkey("F13", lambda: ahk.message_box("Boop"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)

    beep_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Beep")
    boop_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Boop")

    ahk.send("{F13}")
    assert beep_windows.wait(timeout=1)
    assert not boop_windows.exist()

    ahk.send("{F13}")
    assert boop_windows.wait(timeout=1)
    assert beep_windows.exist()

    ahk.send("{F24}")


def test_failing_hotkey_context(child_ahk):
    def code():
        import ahkpy as ahk
        ctx = ahk.HotkeyContext(lambda: ahk.windows.get_active(class_name="Shell_TrayWnd"))
        ctx.hotkey("F13", lambda: ahk.message_box("Boop"))
        print("ok00")

    child_ahk.popen_code(code)
    child_ahk.wait(0)

    boop_windows = ahk.windows.filter(exe="AutoHotkey.exe", text="Boop")

    ahk.send("{F13}")
    assert not boop_windows.wait(timeout=0.1)

    ahk.windows.activate(class_name="Shell_TrayWnd")
    ahk.send("{F13}")
    with pytest.xfail():
        assert boop_windows.wait(timeout=1)

    ahk.send("{F24}")


def test_key_wait(child_ahk):
    def code():
        import ahkpy as ahk
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

    proc = child_ahk.popen_code(code)

    child_ahk.wait(0)
    ahk.send("{RShift Down}")
    child_ahk.wait(1)
    ahk.send("{RShift Up}")
    child_ahk.wait(2)

    child_ahk.wait(3)
    child_ahk.close()
    assert proc.returncode == 0


def test_send_level(child_ahk):
    with pytest.raises(ValueError, match="level must be between 0 and 100"):
        ahk.send("{F13}", level=-1)
    with pytest.raises(ValueError, match="level must be between 0 and 100"):
        ahk.send("{F13}", level=101)

    called = False

    @ahk.hotkey("F15", input_level=10)
    def f15():
        nonlocal called
        called = True

    ahk.send("{F15}")
    ahk.sleep(0)  # Let AHK process the hotkey.
    assert not called

    ahk.send("{F15}", level=20)
    ahk.sleep(0)
    assert called


def test_remap_key(child_ahk):
    def hotkeys():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)

        @ahk.hotkey("F14")
        def trigger():
            ahk.message_box("F14 pressed")

        print("ok00")

    child_ahk.popen_code(hotkeys)
    child_ahk.wait(0)

    remap = ahk.remap_key("F13", "F14")
    ahk.send("{F13}", level=10)
    assert ahk.windows.wait(exe="AutoHotkey.exe", text="F14 pressed", timeout=1)

    remap.disable()

    ahk.send("{F24}", level=10)
