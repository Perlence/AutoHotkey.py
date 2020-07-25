import uuid

import ahkpy as ahk


def test_clipboard(request):
    stored = ahk.get_clipboard()
    request.addfinalizer(lambda: ahk.set_clipboard(stored))

    ahk.set_clipboard("")
    assert ahk.get_clipboard() == ""

    text = str(uuid.uuid4())
    ahk.set_clipboard(text)
    assert ahk.get_clipboard() == text
