import ctypes
import sys
import time

import pytest

import ahkpy as ahk
from .conftest import assert_equals_eventually


skip_unless_admin = pytest.mark.skipif(
    not ctypes.windll.shell32.IsUserAnAdmin(),
    reason="This test requires admin permissions",
)


def test_get_key_state(child_ahk):
    with pytest.raises(ValueError, match="'beep' is not a valid key or the state of the key could not be determined"):
        ahk.is_key_pressed("beep")

    assert ahk.is_key_pressed("F13") is False
    ahk.send("{F13 Down}")
    assert ahk.is_key_pressed("F13") is True
    ahk.send("{F13 Up}")
    assert ahk.is_key_pressed("F13") is False


def test_lock_state(request):
    initial_state = ahk.get_caps_lock_state()
    assert isinstance(initial_state, bool)
    request.addfinalizer(lambda: ahk.set_caps_lock_state(initial_state))

    ahk.set_caps_lock_state(True)
    assert ahk.get_caps_lock_state() is True
    ahk.set_caps_lock_state(False)
    assert ahk.get_caps_lock_state() is False


def test_hotkey_refcounts(request):
    func1 = lambda: None  # noqa: E731
    func2 = lambda: None  # noqa: E731
    func1_refcount = sys.getrefcount(func1)
    func2_refcount = sys.getrefcount(func2)

    hk = ahk.hotkey("F13", func1)
    request.addfinalizer(hk.disable)
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

    hk2 = ahk.hotkey("F14", func1)
    request.addfinalizer(hk2.disable)
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount

    hk2.update(func=func2)
    assert sys.getrefcount(func1) == func1_refcount + 1
    assert sys.getrefcount(func2) == func2_refcount + 1


class TestHotkey:
    def test_exceptions(self):
        with pytest.raises(ahk.Error, match="invalid key name"):
            ahk.hotkey("")

        with pytest.raises(TypeError, match="must be callable"):
            ahk.hotkey("^t", func="not callable")

    def test_hotkey_field(self, request):
        hk = ahk.hotkey("F13", lambda: None)
        request.addfinalizer(hk.disable)
        assert hk.key_name == "F13"

    def test_reenable_on_init(self, request):
        hk = ahk.hotkey("F13", lambda: None)
        request.addfinalizer(hk.disable)
        hk.disable()

        called = False

        @ahk.hotkey("F13")
        def hk2():
            nonlocal called
            called = True

        request.addfinalizer(hk2.disable)

        assert not called
        ahk.send("{F13}", level=1)
        ahk.sleep(0)
        assert called

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
    @pytest.fixture(autouse=True)
    def send_level(self, settings):
        settings.send_level = 10
        # Typing via the default "input" mode doesn't trigger hotstrings because
        # hotstrings use keyboard hook to monitor key strokes and SendInput
        # temporarily deactivates that hook.
        settings.send_mode = "event"

    @pytest.fixture
    def edit(self, notepad):
        edit = notepad.get_control("Edit1")
        edit.text = ""
        assert edit.text == ""
        yield edit
        edit.text = ""
        assert edit.text == ""

    def test_simple(self, request, edit):
        dashes = ahk.hotstring("nepotism", "msitopen")
        request.addfinalizer(dashes.disable)
        ahk.send("nepotism")
        assert_equals_eventually(lambda: edit.text, "nepotism")
        ahk.send(" ")
        assert_equals_eventually(lambda: edit.text, "msitopen ")

    def test_wait_for_and_omit_end_char(self, request, edit):
        jsmith = ahk.hotstring("j@", "jsmith@somedomain.com", wait_for_end_char=False)
        request.addfinalizer(jsmith.disable)
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com")

        edit.text = ""
        jsmith.update(wait_for_end_char=False, omit_end_char=False)
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com")

        edit.text = ""
        jsmith.update(wait_for_end_char=False, omit_end_char=True)
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com")

        edit.text = ""
        jsmith.update(omit_end_char=False)  # wait_for_end_char=False implied
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com")

        edit.text = ""
        jsmith.update(omit_end_char=True)
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send(" ")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com")

        edit.text = ""
        jsmith.update(wait_for_end_char=True)  # omit_end_char implied
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send(" ")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com")

        edit.text = ""
        jsmith.update(wait_for_end_char=True, omit_end_char=False)
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send(" ")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com ")

        edit.text = ""
        jsmith.update(wait_for_end_char=True, omit_end_char=True)
        ahk.send("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send(" ")
        assert_equals_eventually(lambda: edit.text, "jsmith@somedomain.com")

        edit.text = ""
        dashes = ahk.hotstring("crabwise", "esiwbarc")
        request.addfinalizer(dashes.disable)
        dashes.update(wait_for_end_char=False)
        ahk.send("crabwise")
        assert_equals_eventually(lambda: edit.text, "esiwbarc")

        edit.text = ""
        dashes.update(wait_for_end_char=True)
        ahk.send("crabwise")
        assert_equals_eventually(lambda: edit.text, "crabwise")
        ahk.send(" ")
        assert_equals_eventually(lambda: edit.text, "esiwbarc ")

    def test_on_off(self, request, edit):
        beep = ahk.hotstring("beep", "boop")
        request.addfinalizer(beep.disable)
        ahk.send("Beep ")
        assert_equals_eventually(lambda: edit.text, "Boop ")

        edit.text = ""
        beep.disable()
        ahk.send("Beep ")
        assert_equals_eventually(lambda: edit.text, "Beep ")

        edit.text = ""
        beep.enable()
        ahk.send("Beep ")
        assert_equals_eventually(lambda: edit.text, "Boop ")

        edit.text = ""
        beep.toggle()
        ahk.send("Beep ")
        assert_equals_eventually(lambda: edit.text, "Beep ")

    def test_case_sensitive(self, request, edit):
        case = ahk.hotstring("CaSe", "EsAc", case_sensitive=True)
        request.addfinalizer(case.disable)
        ahk.send("case ")
        assert_equals_eventually(lambda: edit.text, "case ")
        ahk.send("CaSe ")
        assert_equals_eventually(lambda: edit.text, "case EsAc ")

    def test_decorator(self, request, edit):
        @ahk.hotstring("blarp")
        def blarp():
            ahk.send("boop ")

        request.addfinalizer(blarp.disable)
        ahk.send("blarp")
        assert_equals_eventually(lambda: edit.text, "blarp")
        ahk.send(" ")
        assert_equals_eventually(lambda: edit.text, "boop ")

    def test_replace_inside_word(self, request, edit):
        airline = ahk.hotstring("al", "airline", replace_inside_word=True)
        request.addfinalizer(airline.disable)
        ahk.send("practical ")
        assert_equals_eventually(lambda: edit.text, "practicairline ")

    def test_no_backspacing(self, request, edit):
        em = ahk.hotstring("<em>", "</em>{left 5}", wait_for_end_char=False, backspacing=False)
        request.addfinalizer(em.disable)
        ahk.send("hello <em>world")
        assert_equals_eventually(lambda: edit.text, "hello <em>world</em>")

    def test_conform_to_case(self, request, edit):
        pillow = ahk.hotstring("pillow", "wollip", conform_to_case=False)
        request.addfinalizer(pillow.disable)
        ahk.send("pillow ")
        assert_equals_eventually(lambda: edit.text, "wollip ")

        edit.text = ""
        ahk.send("PILLOW ")
        assert_equals_eventually(lambda: edit.text, "wollip ")

        edit.text = ""
        ahk.send("PiLLoW ")
        assert_equals_eventually(lambda: edit.text, "wollip ")

    def test_reset_recognizer(self, request, edit):
        @ahk.hotstring("11", backspacing=False, wait_for_end_char=False, replace_inside_word=True)
        def eleven():
            ahk.send("xx", level=0)

        request.addfinalizer(eleven.disable)
        ahk.send("11")
        assert_equals_eventually(lambda: edit.text, "11xx")
        ahk.send("1 ")
        assert_equals_eventually(lambda: edit.text, "11xx1 xx")

        edit.text = ""
        eleven.update(reset_recognizer=True)
        ahk.send("11")
        assert_equals_eventually(lambda: edit.text, "11xx")
        ahk.send("1 ")
        assert_equals_eventually(lambda: edit.text, "11xx1 ")

    def test_text(self, request, edit):
        gyre = ahk.hotstring("gyre", "{F13}eryg", text=True)
        request.addfinalizer(gyre.disable)
        ahk.send("gyre ")
        assert_equals_eventually(lambda: edit.text, "{F13}eryg ")

    def test_active_window_context(self, request, edit):
        notepad_ctx = ahk.windows.active_window_context(class_name="Notepad")
        padnote = notepad_ctx.hotstring("notepad", "padnote")
        request.addfinalizer(padnote.disable)
        ahk.send("notepad ")
        assert_equals_eventually(lambda: edit.text, "padnote ")

    def test_reset_hotstring(self, request, edit):
        malaise = ahk.hotstring("malaise", "redacted")
        request.addfinalizer(malaise.disable)
        ahk.send("malaise ")
        assert_equals_eventually(lambda: edit.text, "redacted ")

        edit.text = ""
        ahk.send("mala")
        ahk.reset_hotstring()
        ahk.send("ise ")
        assert_equals_eventually(lambda: edit.text, "malaise ")

    def test_end_chars(self, request, edit):
        vivacious = ahk.hotstring("vivacious", "redacted")
        request.addfinalizer(vivacious.disable)
        prior_end_chars = ahk.get_hotstring_end_chars()
        request.addfinalizer(lambda: ahk.set_hotstring_end_chars(prior_end_chars))
        ahk.set_hotstring_end_chars(".")
        assert ahk.get_hotstring_end_chars() == "."

        ahk.send("vivacious ")
        assert_equals_eventually(lambda: edit.text, "vivacious ")

        edit.text = ""
        ahk.send("vivacious.")
        assert_equals_eventually(lambda: edit.text, "redacted.")

    def test_mouse_reset(self, request, edit):
        ferret = ahk.hotstring("ferret", "redacted")
        request.addfinalizer(ferret.disable)
        prior_mouse_reset = ahk.get_hotstring_mouse_reset()
        request.addfinalizer(lambda: ahk.set_hotstring_mouse_reset(prior_mouse_reset))

        ahk.send("fer")
        ahk.mouse_move(x=0, y=0)
        ahk.click()
        ahk.send("ret ")
        assert_equals_eventually(lambda: edit.text, "ferret ")

        edit.text = ""
        ahk.set_hotstring_mouse_reset(False)
        ahk.get_hotstring_mouse_reset() is False
        ahk.send("fer")
        ahk.mouse_move(x=0, y=0)
        ahk.click()
        ahk.send("ret ")
        assert_equals_eventually(lambda: edit.text, "redacted ")


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


def test_key_wait(child_ahk):
    def code():
        import ahkpy as ahk
        import sys

        print("ok00")
        result = ahk.wait_key_pressed("RShift")
        assert result is True, "result must be True"
        print("ok01")
        result = ahk.wait_key_released("RShift")
        assert result is True, "result must be True"
        print("ok02")

        result = ahk.wait_key_pressed("RShift", timeout=.1)
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

    # Use SendEvent here because hotkeys with input_level > 0 use keyboard hook
    # and SendInput temporarily disables that hook.
    ahk.send_event("{F15}")
    ahk.sleep(0)  # Let AHK process the hotkey.
    assert not called

    ahk.send_event("{F15}", level=20)
    ahk.sleep(0)
    assert called


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


def test_fallback_to_send_event_on_delay(notepad):
    start = time.perf_counter()
    ahk.send("abcdef", key_delay=0.01)
    end = time.perf_counter()
    assert end - start >= 6 * 0.01


def test_get_key():
    key = "LWin"
    assert ahk.get_key_name(key) == "LWin"
    assert ahk.get_key_vk(key) == 0x5b
    assert ahk.get_key_sc(key) == 0x15b
    assert ahk.get_key_name("vk5b") == "LWin"
    assert ahk.get_key_name("sc15b") == "LWin"

    assert ahk.get_key_name(1) == "1"

    with pytest.raises(ValueError, match="is not a valid key"):
        ahk.get_key_vk("noooo")


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
