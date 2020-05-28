import _ahk  # noqa


def message_box(text=None, title="", options=0, timeout=None):
    if text is None:
        # Show "Press OK to continue."
        return _ahk.call("MsgBox")

    return _ahk.call("MsgBox", options, title, str(text), timeout)
    # TODO: Return result of IfMsgBox?
