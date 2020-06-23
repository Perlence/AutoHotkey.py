import ahk


def test_message_box(child_ahk):
    def msg_boxes_code():
        import ahk
        ahk.message_box()
        ahk.message_box("Hello, мир!")
        ahk.message_box("Hello, 世界")
        ahk.message_box("Do you want to continue? (Press YES or NO)", options=4)

    child_ahk.popen_code(msg_boxes_code)
    ahk.set_win_delay(None)

    msg_boxes = ahk.windows.filter(exe="AutoHotkey.exe")

    msg_box = msg_boxes.wait_active(text="Press OK to continue", timeout=1)
    assert msg_box
    msg_box.send("{Enter}")

    msg_box = msg_boxes.wait_active(text="Hello, мир!", timeout=1)
    assert msg_box
    msg_box.send("{Enter}")

    msg_box = msg_boxes.wait_active(text="Hello, 世界", timeout=1)
    assert msg_box
    msg_box.send("{Enter}")

    msg_box = msg_boxes.wait_active(text="Do you want to continue? (Press YES or NO)", timeout=1)
    assert msg_box
    assert "&Yes" in msg_box.text
    assert "&No" in msg_box.text
    msg_box.send("{Enter}")
