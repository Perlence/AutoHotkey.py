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

    request.addfinalizer(handler.disable)

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

    request.addfinalizer(prepended_handler.disable)

    history.clear()
    ahk.set_clipboard("hey")
    ahk.sleep(0)
    assert history == ["HEY", "hey"]

    @ahk.on_clipboard_change()
    def exclamator(clipboard):
        history.append(clipboard + "!!")

    request.addfinalizer(exclamator.disable)

    history.clear()
    ahk.set_clipboard("yay")
    ahk.sleep(0)
    assert history == ["YAY", "yay", "yay!!"]

    history.clear()
    handler.disable()
    ahk.set_clipboard("hello again")
    ahk.sleep(0.1)
    assert history == ["HELLO AGAIN", "hello again!!"]
