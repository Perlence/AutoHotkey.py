import ahk


def test_message_box():
    result = ahk.message_box()
    assert result == "", "MsgBox result must be an empty string"
    ahk.message_box("Hello, мир!")
    ahk.message_box("Do you want to continue? (Press YES or NO)", options=4)
