import sys
from unittest.mock import call

import pytest

import ahkpy as ahk
import _ahk


def noop():
    pass


@pytest.fixture
def call_spy(mocker):
    return mocker.spy(_ahk, "call")


@pytest.fixture
def menu(request):
    menu = ahk.Menu()
    yield menu
    menu.delete_menu()


def test_get_handle(menu):
    menu.add("Test", noop)
    handle = menu.get_handle()
    assert isinstance(handle, int)


def test_add(call_spy, menu):
    res = menu.add("E&xit", sys.exit, default=True, icon="c:/Windows/py.exe", icon_number=1)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "E&xit", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
        call("Menu", menu.name, "Default", "E&xit"),
        call("Menu", menu.name, "Icon", "E&xit", "c:/Windows/py.exe", 2, None)
    ])
    assert res is menu

    call_spy.reset_mock()
    menu.remove_default()
    call_spy.assert_has_calls([
        call("Menu", menu.name, "NoDefault"),
    ])

    call_spy.reset_mock()
    menu.add("Radio", lambda: menu.toggle_checked("Radio"), radio=True)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "Radio", call_spy.mock_calls[0][1][5], "P0 +Radio -Break -BarBreak"),
    ])

    call_spy.reset_mock()
    res = menu.add_separator()
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert"),
    ])
    assert res is menu

    submenu = ahk.Menu()
    call_spy.reset_mock()
    submenu.add("I1", noop)
    call_spy.assert_has_calls([
        call("Menu", submenu.name, "Insert", None, "I1", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
    ])

    call_spy.reset_mock()
    res = menu.add_submenu("Sub", submenu)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "Sub", f":{submenu.name}", "-Radio -Break -BarBreak"),
    ])
    assert res is menu

    call_spy.reset_mock()
    menu.add("NewCol", noop, new_column=True)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "NewCol", call_spy.mock_calls[0][1][5], "P0 -Radio +Break -BarBreak"),
    ])

    call_spy.reset_mock()
    menu.add("NewCol", noop, new_column=True, checked=True)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "NewCol", call_spy.mock_calls[0][1][5], "P0 -Radio +Break -BarBreak"),
        call("Menu", menu.name, "Check", "NewCol"),
    ])

    call_spy.reset_mock()
    menu.add("Dis", noop, enabled=False)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "Dis", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
        call("Menu", menu.name, "Disable", "Dis"),
    ])


def test_chaining(call_spy):
    submenu = (
        ahk.Menu()
        .add("S1", noop)
        .add("S2", noop)
    )
    call_spy.assert_has_calls([
        call("Menu", submenu.name, "Insert", None, "S1", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
        call("Menu", submenu.name, "Insert", None, "S2", call_spy.mock_calls[1][1][5], "P0 -Radio -Break -BarBreak"),
    ])

    call_spy.reset_mock()
    menu = (
        ahk.Menu()
        .add("Item1", noop)
        .add("Item2", noop)
        .add_separator()
        .add_submenu(
            "My Submenu",
            submenu,
        )
        .add_separator()
        .add("Item3", noop)
    )
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "Item1", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
        call("Menu", menu.name, "Insert", None, "Item2", call_spy.mock_calls[1][1][5], "P0 -Radio -Break -BarBreak"),
        call("Menu", menu.name, "Insert"),
        call("Menu", menu.name, "Insert", None, "My Submenu", f":{submenu.name}", "-Radio -Break -BarBreak"),
        call("Menu", menu.name, "Insert"),
        call("Menu", menu.name, "Insert", None, "Item3", call_spy.mock_calls[5][1][5], "P0 -Radio -Break -BarBreak")
    ])


def test_insert(call_spy, menu):
    menu.add("Test", noop)

    with pytest.raises(TypeError, match="insert_before must not be None"):
        menu.insert(None, "Test")

    call_spy.reset_mock()
    menu.insert("Test", "2&", noop)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", "Test", "2&", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
    ])

    call_spy.reset_mock()
    menu.insert(1, "2&", noop)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", "2&", "2&", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
    ])


def test_insert_submenu(call_spy, menu):
    menu.add("Test", noop)
    submenu = ahk.Menu().add("Nooo", noop)

    with pytest.raises(TypeError, match="insert_before must not be None"):
        menu.insert_submenu(None, "Sub", submenu)

    call_spy.reset_mock()
    menu.insert_submenu("Test", "Sub", submenu)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", "Test", "Sub", f":{submenu.name}", '-Radio -Break -BarBreak'),
    ])


def test_insert_separator(call_spy, menu):
    menu.add("Test", noop)

    with pytest.raises(TypeError, match="insert_before must not be None"):
        menu.insert_separator(None)

    call_spy.reset_mock()
    menu.insert_separator("Test")
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", "Test"),
    ])


def test_update(call_spy, menu):
    menu.add("Test", noop)

    with pytest.raises(TypeError, match="item_name must not be None"):
        menu.update(None, new_name="Test")

    call_spy.reset_mock()
    menu.update("Test", callback=noop, radio=True, icon=ahk.executable)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Add", "Test", None, "+Radio"),
        call("Menu", menu.name, "Add", "Test", call_spy.mock_calls[1][1][4]),
    ])

    call_spy.reset_mock()
    menu.update(0, enabled=False)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Disable", "1&"),
    ])

    call_spy.reset_mock()
    menu.update(0, enabled=True)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Enable", "1&"),
    ])

    call_spy.reset_mock()
    menu.toggle_enabled(0)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "ToggleEnable", "1&"),
    ])

    call_spy.reset_mock()
    menu.update(0, checked=True)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Check", "1&"),
    ])

    call_spy.reset_mock()
    menu.update(0, checked=False)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Uncheck", "1&"),
    ])

    call_spy.reset_mock()
    menu.toggle_checked(0)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "ToggleCheck", "1&"),
    ])

    call_spy.reset_mock()
    menu.rename(0, "Renamed")
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Rename", "1&", "Renamed"),
    ])

    call_spy.reset_mock()
    menu.update(0, new_name="New name", callback=lambda: print("New name"))
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Add", "1&", call_spy.mock_calls[0][1][4]),
        call("Menu", menu.name, "Rename", "1&", "New name")
    ])


def test_update_separator(child_ahk):
    def code():
        import ahkpy as ahk

        menu = ahk.Menu()
        menu.add_separator()
        menu.update(0, new_name="Test", callback=lambda: print("ok01"))
        print("ok00")
        menu.show()

    child_ahk.popen_code(code)
    child_ahk.wait(0)

    ahk.sleep(0)
    ahk.send("{Down}{Enter}")
    child_ahk.wait(1)


def test_update_remove_icon(call_spy, menu):
    menu.add("Test", noop, icon=ahk.executable)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Insert", None, "Test", call_spy.mock_calls[0][1][5], "P0 -Radio -Break -BarBreak"),
        call("Menu", menu.name, "Icon", "Test", ahk.executable, 1, None)
    ])

    call_spy.reset_mock()
    menu.update("Test", icon=None)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "NoIcon", "Test")
    ])


def test_update_nonexistent():
    menu = ahk.Menu()
    with pytest.raises(ahk.Error, match="Menu does not exist"):
        menu.update("Nonexistent", new_name="Fails")

    menu.add("Test", noop)
    with pytest.raises(ahk.Error, match="Nonexistent menu item"):
        menu.update("Nonexistent", new_name="Fails")


def test_delete_item(call_spy, menu):
    menu.add("Test", noop)

    menu.delete_item("Test")
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Delete", "Test")
    ])

    menu.add("Test", noop)
    call_spy.reset_mock()
    menu.delete_item(0)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Delete", "1&")
    ])


def test_delete_all_items(call_spy, menu):
    menu.add("Test", noop)

    menu.delete_all_items()
    call_spy.assert_has_calls([
        call("Menu", menu.name, "DeleteAll")
    ])


def test_set_color(call_spy, menu):
    menu.add("Test", lambda: None)

    call_spy.reset_mock()
    menu.set_color("ffffff")
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Color", "ffffff", None)
    ])

    call_spy.reset_mock()
    menu.set_color("ffffff", affects_submenus=False)
    call_spy.assert_has_calls([
        call("Menu", menu.name, "Color", "ffffff", "Single")
    ])


def test_tray_icon(request, call_spy):
    request.addfinalizer(lambda: ahk.tray_menu.set_tray_icon(None))
    request.addfinalizer(lambda: setattr(ahk.tray_menu, "tip", None))

    assert ahk.tray_menu.tray_icon_file is None
    assert ahk.tray_menu.tray_icon_number is None

    call_spy.reset_mock()
    ahk.tray_menu.set_tray_icon(ahk.executable, number=2, affected_by_suspend=True)
    ahk.tray_menu.set_tray_icon(affected_by_suspend=False)
    call_spy.assert_has_calls([
        call("Menu", "tray", "Icon", ahk.executable, 3, "0"),
        call("Menu", "tray", "Icon", "", None, "1")
    ])
    assert ahk.tray_menu.tray_icon_file == ahk.executable
    assert ahk.tray_menu.tray_icon_number == 2

    ahk.tray_menu.tray_icon_file = None
    assert ahk.tray_menu.tray_icon_file is None
    assert ahk.tray_menu.tray_icon_number is None

    ahk.tray_menu.tray_icon_file = ahk.executable
    ahk.tray_menu.tray_icon_number = 2
    assert ahk.tray_menu.tray_icon_file == ahk.executable
    assert ahk.tray_menu.tray_icon_number == 2

    assert ahk.tray_menu.is_tray_icon_visible is True
    ahk.tray_menu.is_tray_icon_visible = False
    assert ahk.tray_menu.is_tray_icon_visible is False
    ahk.tray_menu.is_tray_icon_visible = True
    assert ahk.tray_menu.is_tray_icon_visible is True

    ahk.tray_menu.hide_tray_icon()
    assert ahk.tray_menu.is_tray_icon_visible is False
    ahk.tray_menu.show_tray_icon()
    assert ahk.tray_menu.is_tray_icon_visible is True

    ahk.tray_menu.toggle_tray_icon()
    assert ahk.tray_menu.is_tray_icon_visible is False
    ahk.tray_menu.toggle_tray_icon()
    assert ahk.tray_menu.is_tray_icon_visible is True

    ahk.tray_menu.tip is None
    ahk.tray_menu.tip = "Nooo"
    ahk.tray_menu.tip == "Nooo"
    ahk.tray_menu.tip = None
    ahk.tray_menu.tip is None

    call_spy.reset_mock()
    ahk.tray_menu.set_clicks(1)
    call_spy.assert_has_calls([
        call("Menu", "tray", "Click", 1),
    ])
