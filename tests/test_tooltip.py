import os

import pytest

import ahkpy as ahk


def test_basic(request):
    tooltip_windows = ahk.windows.filter(class_name="tooltips_class32", pid=os.getpid())
    assert not tooltip_windows.exist()

    t1 = ahk.ToolTip()
    request.addfinalizer(t1.hide)
    t1.show("hello", x=0, y=0)
    assert tooltip_windows.exist()

    t1.hide()
    assert not tooltip_windows.exist()


def test_exceptions(request):
    with pytest.raises(ValueError, match="text must not be empty"):
        ahk.ToolTip().show()

    with pytest.raises(ValueError, match="is not a valid coord mode"):
        ahk.ToolTip(relative_to="nooo")


def test_too_many_tooltips(request):
    tooltips = []
    for i in range(1, 21):
        t = ahk.ToolTip(i, relative_to="screen")
        request.addfinalizer(t.hide)
        t.show(x=50*i, y=50*i)
        tooltips.append(t)

    with pytest.raises(RuntimeError, match="cannot show more than 20 tooltips"):
        ahk.ToolTip().show("21")


def test_timeout(request):
    t = ahk.ToolTip("test")
    request.addfinalizer(t.hide)

    tooltips = ahk.windows.filter(class_name="tooltips_class32", pid=os.getpid())

    t.show(timeout=0.1)
    assert tooltips.exist()
    ahk.sleep(0.11)
    assert not tooltips.exist()

    t.show(timeout=0.1)
    t.show()  # This must cancel the timeout.
    assert tooltips.exist()
    ahk.sleep(0.11)
    assert tooltips.exist()

    t.show()
    t.show(timeout=0.1)
    assert tooltips.exist()
    ahk.sleep(0.11)
    assert not tooltips.exist()

    t.show(timeout=0.1)
    ahk.sleep(0.06)
    t.show(timeout=0.1)  # This must reset the timeout.
    assert tooltips.exist()
    ahk.sleep(0.06)
    assert tooltips.exist()
    ahk.sleep(0.06)
    assert not tooltips.exist()
