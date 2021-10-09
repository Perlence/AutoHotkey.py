import sys

import ahkpy as ahk


def test_clipboard(request, child_ahk):
    stored = ahk.get_clipboard()
    request.addfinalizer(lambda: ahk.set_clipboard(stored))

    def code():
        import ahkpy as ahk
        ahk.sleep(0.1)
        ahk.set_clipboard("hello from ahk")

    ahk.set_clipboard("")
    assert ahk.get_clipboard() == ""

    child_ahk.popen_code(code)
    assert ahk.wait_clipboard() == "hello from ahk"

    ahk.set_clipboard("")
    assert ahk.wait_clipboard(timeout=0.1) == ""


def test_on_clipboard_change(request):
    stored = ahk.get_clipboard()
    request.addfinalizer(lambda: ahk.set_clipboard(stored))

    history = []

    @ahk.on_clipboard_change
    def handler(clipboard):
        history.append(clipboard)

    request.addfinalizer(handler.unregister)

    ahk.set_clipboard("")
    ahk.sleep(0)
    assert history == [""]

    history.clear()
    ahk.set_clipboard("hello")
    ahk.sleep(0)
    assert history == ["hello"]

    @ahk.on_clipboard_change(prepend_handler=True)
    def prepended_handler(clipboard):
        history.append(clipboard.upper())

    request.addfinalizer(prepended_handler.unregister)

    history.clear()
    ahk.set_clipboard("hey")
    ahk.sleep(0)
    assert history == ["HEY", "hey"]

    @ahk.on_clipboard_change()
    def exclamator(clipboard):
        history.append(clipboard + "!!")

    request.addfinalizer(exclamator.unregister)

    history.clear()
    ahk.set_clipboard("yay")
    ahk.sleep(0)
    assert history == ["YAY", "yay", "yay!!"]

    history.clear()
    handler_func = handler.func
    handler_func_refcount = sys.getrefcount(handler_func)
    handler.unregister()
    assert sys.getrefcount(handler_func) == handler_func_refcount - 1

    ahk.set_clipboard("hello again")
    ahk.sleep(0.1)
    assert history == ["HELLO AGAIN", "hello again!!"]


def test_clipboard_returns(request, child_ahk):
    stored = ahk.get_clipboard()
    request.addfinalizer(lambda: ahk.set_clipboard(stored))

    def clipboards():
        import ahkpy as ahk
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.on_clipboard_change()
        def objector():
            return object()

        print("ok00")

    child_ahk.popen_code(clipboards)
    child_ahk.wait(0)

    ahk.set_clipboard("371")
    assert not ahk.windows.wait(
        title="Python.ahk",
        text="Error:  cannot convert '<object object",
        timeout=0.1,
    )
    assert ahk.get_clipboard() == "371"

    ahk.send("{F24}")
