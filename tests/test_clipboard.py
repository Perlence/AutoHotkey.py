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
