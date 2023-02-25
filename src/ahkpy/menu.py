import dataclasses as dc
import functools
import uuid

from .flow import ahk_call, global_ahk_lock, _wrap_callback
from .settings import COORD_MODES, _set_coord_mode
from .unset import UNSET


__all__ = [
    "Menu",
    "TrayMenu",
    "tray_menu",
]


@dc.dataclass(frozen=True)
class Menu:
    """The menu object.

    Can be used to create, modify, and show menus.

    The optional *name* argument identifies the menu. If omitted, a random name
    is generated.

    Example usage::

       def menu_handler(item_name, item_pos, menu):
           ahkpy.message_box(f"You selected {item_name} from {menu}.")

       # Create the popup menu by adding some items to it.
       menu = ahkpy.Menu()
       menu.add("Item1", menu_handler)
       menu.add("Item2", menu_handler)
       menu.add_separator()

       # Create another menu destined to become a submenu of the above menu.
       submenu = ahkpy.Menu()
       submenu.add("Item1", menu_handler)
       submenu.add("Item2", menu_handler)

       # Create a submenu in the first menu (a right-arrow indicator). When the
       # user selects it, the second menu is displayed.
       menu.add_submenu("My Submenu", submenu)

       # Add more items beneath the submenu.
       menu.add_separator()
       menu.add("Item3", menu_handler)

       ahk.hotkey("F1", menu.show)

    The :class:`!Menu` instances also support the chaining API. The above
    example can be written as follows::

       def menu_handler(item_name, menu, **kw):
           ahkpy.message_box(f"You selected {item_name} from {menu}.")

       menu = (
           ahkpy.Menu()
           .add("Item1", menu_handler)
           .add("Item2", menu_handler)
           .add_separator()
           .add_submenu(
               "My Submenu",
               ahkpy.Menu()
               .add("Item1", menu_handler)
               .add("Item2", menu_handler)
           )
           .add_separator()
           .add("Item3", menu_handler)
       )

       ahk.hotkey("F1", menu.show)
    """

    name: str
    __slots__ = ("name",)

    def __init__(self, name: str = None):
        if name is None:
            name = str(uuid.uuid4())
        object.__setattr__(self, "name", name.lower())

    def get_handle(self) -> int:
        """Retrieve the Win32 menu handle of a menu (HMENU).

        :command: `MenuGetHandle
           <https://www.autohotkey.com/docs/commands/MenuGetHandle.htm>`_
        """
        return ahk_call("MenuGetHandle", self.name)

    def add(
        self, item_name, callback, *args,
        priority=0, default=False, enabled=True, checked=False,
        radio=False, new_column=False, bar_column=False,
        icon=UNSET, icon_number=None, icon_width=None,
    ):
        """add(item_name, callback, *args, priority=0, **options)

        Append a menu item *item_name*.

        When the user selects the menu item, the *callback* function is called
        with *item_name*, *item_pos*, and *menu* arguments.

        The optional positional *args* will be passed to the *callback* when it
        is called. If you want the *callback* to be called with keyword
        arguments use :func:`functools.partial`.

        The optional *priority* argument sets the priority of the `AHK thread
        <https://www.autohotkey.com/docs/misc/Threads.htm>`_ where *callback*
        will be executed. It must be an :class:`int` between -2147483648 and
        2147483647. Defaults to 0.

        The following keyword-only arguments set the menu item *options*:

        :param bool default: if true, the menu item is promoted to a
           default one for the menu. Defaults to ``False``.

        :param bool enabled: if false, the menu item is disabled. Enabled by
           default.

        :param bool checked: if true, the menu item is checked. Defaults to
           ``False``.

        :param bool radio: if true, a bullet point is used instead of a check
           mark when the item is checked. Defaults to ``False``.

        :param bool new_column: if true, the item begins a new column in a popup
           menu. Defaults to ``False``.

        :param bool bar_column: if true, the item begins a new column in a popup
           menu divided by a vertical bar. Defaults to ``False``.

        :param str icon: along with the *icon_number* and *icon_width* arguments
           set an icon for the specified menu item. For more details refer to
           :meth:`set_icon`. To remove the icon, pass ``None`` to *icon*.

        :command: `Menu, $, Add, MenuItemName, %FuncObj%, Options
           <https://www.autohotkey.com/docs/commands/Menu.htm#Insert>`_
        """
        return self._insert_or_update(
            None, item_name, callback=callback, args=args,
            priority=priority, default=default, enabled=enabled, checked=checked,
            radio=radio, new_column=new_column, bar_column=bar_column,
            icon=icon, icon_number=icon_number, icon_width=icon_width,
        )

    def add_separator(self):
        """Append a separator.

        :command: `Menu, $, Add
           <https://www.autohotkey.com/docs/commands/Menu.htm#Insert>`_
        """
        self._call("Insert")
        return self

    def add_submenu(
        self, item_name, submenu: 'Menu', *,
        default=False, enabled=True, checked=False,
        radio=False, new_column=False, bar_column=False,
        icon=UNSET, icon_number=None, icon_width=None,
    ):
        """add_submenu(item_name, submenu: Menu, **options)

        Append a submenu named *item_name*.

        For *options* refer to :meth:`add`.

        :command: `Menu, $, Add, MenuItemName, :Submenu, Options
           <https://www.autohotkey.com/docs/commands/Menu.htm#Insert>`_
        """
        return self._insert_or_update(
            None, item_name, submenu=submenu,
            default=default, enabled=enabled, checked=checked,
            radio=radio, new_column=new_column, bar_column=bar_column,
            icon=icon, icon_number=icon_number, icon_width=icon_width,
        )

    def insert(
        self, insert_before, item_name=None, callback=None, *args,
        priority=0, default=False, enabled=True, checked=False,
        radio=False, new_column=False, bar_column=False,
        icon=UNSET, icon_number=None, icon_width=None,
    ):
        """insert(insert_before, item_name, callback, *args, priority=0, **options)

        Insert a menu item *item_name* before the item referred to by *insert_before*.

        The *insert_before* argument can be either menu item's name or its
        position number.

        When the user selects the menu item, the *callback* function is called
        with *item_name*, *item_pos*, and *menu* arguments.

        The optional positional *args* will be passed to the *callback* when it
        is called. If you want the *callback* to be called with keyword
        arguments use :func:`functools.partial`.

        The optional *priority* argument sets the priority of the `AHK thread
        <https://www.autohotkey.com/docs/misc/Threads.htm>`_ where *callback*
        will be executed. It must be an :class:`int` between -2147483648 and
        2147483647. Defaults to 0.

        For *options* refer to :meth:`add`.

        :command: `Menu, $, Insert, InsertBefore, MenuItemName, %FuncObj%,
           Options <https://www.autohotkey.com/docs/commands/Menu.htm#Insert>`_
        """
        if insert_before is None:
            raise TypeError("insert_before must not be None")
        return self._insert_or_update(
            insert_before, item_name, callback=callback, args=args,
            priority=priority, default=default, enabled=enabled, checked=checked,
            radio=radio, new_column=new_column, bar_column=bar_column,
            icon=icon, icon_number=icon_number, icon_width=icon_width,
        )

    def insert_separator(self, insert_before):
        """
        Insert a separator before the item referred to by *insert_before*.

        The *insert_before* argument can be either menu item's name or its
        position number.

        :command: `Menu, $, Insert, InsertBefore
           <https://www.autohotkey.com/docs/commands/Menu.htm#Insert>`_
        """
        if insert_before is None:
            raise TypeError("insert_before must not be None")
        insert_before = self._item_name(insert_before)
        self._call("Insert", insert_before)
        return self

    def insert_submenu(
        self, insert_before, item_name, submenu: 'Menu', *,
        default=False, enabled=True, checked=False,
        radio=False, new_column=False, bar_column=False,
        icon=UNSET, icon_number=None, icon_width=None,
    ):
        """insert_submenu(insert_before, item_name, submenu: Menu, **options)

        Insert a submenu named *item_name* before the item referred to by
        *insert_before*.

        The *insert_before* argument can be either menu item's name or its
        position number.

        For *options* refer to :meth:`add`.

        :command: `Menu, $, Insert, InsertBefore, :Submenu, Options
           <https://www.autohotkey.com/docs/commands/Menu.htm#Insert>`_
        """
        if insert_before is None:
            raise TypeError("insert_before must not be None")
        return self._insert_or_update(
            insert_before, item_name, submenu=submenu,
            default=default, enabled=enabled, checked=checked,
            radio=radio, new_column=new_column, bar_column=bar_column,
            icon=icon, icon_number=icon_number, icon_width=icon_width,
        )

    def update(
        self, item_name, *, new_name=UNSET, callback=None, submenu=None,
        priority=None, enabled=None, checked=None,
        radio=None, new_column=None, bar_column=None,
        icon=UNSET, icon_number=None, icon_width=None,
    ):
        """update(item_name, *, new_name=UNSET, callback=None, submenu=None, priority=None, **options)

        Update an existing menu item.

        The *item_name* argument can be either menu item's name or its position
        number.

        To rename the menu item, specify the *new_name* argument. To convert the
        menu item to a separator, pass ``None`` to *new_name*.

        To convert a regular menu item to submenu, specify the *submenu*
        argument. To convert a separator to a menu item, specify its position
        and pass the *new_name*.

        For *options* refer to :meth:`add`, with the only exception of the
        *default* argument. To change the default item of the menu, use
        :meth:`set_default` and :meth:`remove_default`.

        :command: `Menu, $, Add, MenuItemName, LabelOrSubmenu, Options
           <https://www.autohotkey.com/docs/commands/Menu.htm#Add>`_
        """
        if item_name is None:
            raise TypeError("item_name must not be None")
        self._insert_or_update(
            item_name, new_name, callback=callback, submenu=submenu,
            update=True,
            priority=priority, enabled=enabled, checked=checked,
            radio=radio, new_column=new_column, bar_column=bar_column,
            icon=icon, icon_number=icon_number, icon_width=icon_width,
        )

    def _insert_or_update(
        self, item_name=None, new_name=UNSET, *, callback=None, args=(), submenu=None,
        update=False,
        priority=None, default=False, enabled=True, checked=False,
        radio=None, new_column=None, bar_column=None,
        icon=UNSET, icon_number=None, icon_width=None,
    ):
        item_name = self._item_name(item_name)

        if submenu is not None:
            thing = f":{submenu.name}"
        elif callback is not None:
            thing = _wrap_callback(
                functools.partial(callback, *args),
                ("item_name", "item_pos", "menu"),
                _bare_menu_item_handler,
                _menu_item_handler,
            )
        else:
            thing = None

        option_list = []
        if priority is not None:
            option_list.append(f"P{priority}")
        if radio is not None:
            option_list.append(f"{'+' if radio else '-'}Radio")
        if new_column is not None:
            option_list.append(f"{'+' if new_column else '-'}Break")
        if bar_column is not None:
            option_list.append(f"{'+' if bar_column else '-'}BarBreak")
        option_str = " ".join(option_list)

        if update:
            # Update separately. If the menu item doesn't exist, setting the
            # options will fail.
            if option_str:
                self._call("Add", item_name, None, option_str)
            if thing is not None:
                self._call("Add", item_name, thing)
            if enabled:
                self.enable(item_name)
            elif enabled is not None:
                self.disable(item_name)
            if checked:
                self.check(item_name)
            elif checked is not None:
                self.uncheck(item_name)
            if icon:
                self.set_icon(item_name, icon, icon_number, icon_width)
            elif icon is None:
                self.remove_icon(item_name)
            if new_name is not UNSET:
                self.rename(item_name, new_name)
        else:
            self._call("Insert", item_name, new_name, thing, option_str)
            if new_name:  # If not a separator
                if default:
                    self.set_default(new_name)
                if not enabled:
                    self.disable(new_name)
                if checked:
                    self.check(new_name)
                if icon:
                    self.set_icon(new_name, icon, icon_number, icon_width)
            return self

    def delete_item(self, item_name):
        """Delete the item from the menu.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, Delete, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#Delete>`_
        """
        item_name = self._item_name(item_name)
        self._call("Delete", item_name)

    def delete_all_items(self):
        """Delete all items from the menu.

        :command: `Menu, $, DeleteAll
           <https://www.autohotkey.com/docs/commands/Menu.htm#DeleteAll>`_
        """
        self._call("DeleteAll")

    def delete_menu(self):
        """Delete the entire menu and any menu items in other menus that use
        this menu as a submenu.

        :command: `Menu, $, Delete
           <https://www.autohotkey.com/docs/commands/Menu.htm#Delete>`_
        """
        self._call("Delete")

    def rename(self, item_name, new_name=None):
        """Rename the menu item.

        The *item_name* argument can be either menu item's name or its position
        number.

        To convert the menu item to a separator, pass ``None`` to *new_name*. To
        convert a separator to a menu item, specify its position and pass the
        *new_name*.

        :command: `Menu, $, Rename, MenuItemName, NewName
           <https://www.autohotkey.com/docs/commands/Menu.htm#Rename>`_
        """
        if item_name is not None:
            item_name = self._item_name(item_name)
        self._call("Rename", item_name, new_name)

    def check(self, item_name):
        """Add a visible checkmark in the menu next to the specified menu item.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, Check, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#Check>`_
        """
        item_name = self._item_name(item_name)
        self._call("Check", item_name)

    def uncheck(self, item_name):
        """Remove the checkmark from the specified menu item.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, Uncheck, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#Uncheck>`_
        """
        item_name = self._item_name(item_name)
        self._call("Uncheck", item_name)

    def toggle_checked(self, item_name):
        """Add a checkmark to the specified menu item if there wasn't one;
        otherwise, remove it.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, ToggleCheck, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#ToggleCheck>`_
        """
        item_name = self._item_name(item_name)
        self._call("ToggleCheck", item_name)

    def enable(self, item_name):
        """Allow the user to select the specified menu item if it was previously
        disabled.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, Enable, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#Enable>`_
        """
        item_name = self._item_name(item_name)
        self._call("Enable", item_name)

    def disable(self, item_name):
        """Change the specified menu item to a gray color to indicate that the
        user cannot select it.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, Disable, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#Disable>`_
        """
        item_name = self._item_name(item_name)
        self._call("Disable", item_name)

    def toggle_enabled(self, item_name):
        """Disable the specified menu item if it was previously enabled;
        otherwise, enable it.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, ToggleEnable, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#ToggleEnable>`_
        """
        item_name = self._item_name(item_name)
        self._call("ToggleEnable", item_name)

    def set_default(self, item_name):
        """Changes the menu's default item to be the specified menu item and
        makes its font bold.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, Default, MenuItemName
           <https://www.autohotkey.com/docs/commands/Menu.htm#Default>`_
        """
        item_name = self._item_name(item_name)
        self._call("Default", item_name)

    def remove_default(self):
        """Convert the default menu item to a regular one.

        :command: `Menu, $, NoDefault
           <https://www.autohotkey.com/docs/commands/Menu.htm#NoDefault>`_
        """
        self._call("NoDefault")

    def _remove_standard(self):
        self._call("NoStandard")

    def set_icon(self, item_name, filename, number=0, width=None):
        """Set an icon for the specified menu item.

        The *item_name* argument can be either menu item's name or its position
        number.

        The *filename* argument can be either an icon file (ICO, CUR, ANI, EXE,
        DLL, CPL, SCR) or any image in a format supported by AutoHotkey. Passing
        ``None`` removes the icon.

        The optional *number* argument sets the icon group to use. It defaults
        to 0, which is the first group in the file. If *number* is negative, its
        absolute value is assumed to be the resource ID of an icon within an
        executable file.

        The optional *width* argument sets the desired width of the icon. If the
        icon group indicated by *number* contains multiple icon sizes, the
        closest match is used and the icon is scaled to the specified size.

        :command: `Menu, $, Icon, MenuItemName, FileName, IconNumber, IconWidth
           <https://www.autohotkey.com/docs/commands/Menu.htm#MenuIcon>`_
        """
        item_name = self._item_name(item_name)
        number = number or 0
        self._call("Icon", item_name, filename, number+1, width)

    def remove_icon(self, item_name):
        """Remove the icon from the specified menu item.

        The *item_name* argument can be either menu item's name or its position
        number.

        :command: `Menu, $, NoIcon, MenuItem
           <https://www.autohotkey.com/docs/commands/Menu.htm#NoIcon>`_
        """
        item_name = self._item_name(item_name)
        self._call("NoIcon", item_name)

    def show(self, x=None, y=None, *, relative_to="window"):
        """Show the menu.

        If the method is called without arguments, the menu is shown at the
        mouse cursor.

        Otherwise, the menu's position depends on the *relative_to* argument.
        Valid *relative_to* values are:

        - ``"screen"`` – coordinates are relative to the desktop (entire
          screen).
        - ``"window"`` – coordinates are relative to the active window.
        - ``"client"`` – coordinates are relative to the active window's client
          area, excluding title bar, menu and borders.

        The optional *x* and *y* arguments set the menu's position relative to
        the area specified by the *relative_to* argument. The default
        *relative_to* value is ``"window"``. So if you call ``menu.show(x=42)``,
        the *y* coordinate will be the mouse cursor's *y* coordinate, and the
        *x* coordinate will be 42 pixels to the right of the active window.

        :command: `Menu, $, Show, X, Y
           <https://www.autohotkey.com/docs/commands/Menu.htm#Show>`_
        """
        if relative_to not in COORD_MODES:
            raise ValueError(f"{relative_to!r} is not a valid coord mode")
        with global_ahk_lock:
            _set_coord_mode("menu", relative_to)
            self._call("Show", x, y)

    def set_color(self, color, affects_submenus=True):
        """Set the background color of the menu.

        The *color* argument accepts one of the 16 primary HTML color names or a
        6-digit hexademical RGB color value.

        To reset the default color, pass ``None`` to *color*.

        If the optional *affects_submenus* argument is false, the submenus
        attached to this menu will not be changed in color. Defaults to
        ``True``.

        :command: `Menu, $, Color, ColorValue
           <https://www.autohotkey.com/docs/commands/Menu.htm#Icon>`_
        """
        single = "Single" if not affects_submenus else None
        self._call("Color", color, single)

    def _item_name(self, name):
        if isinstance(name, int):
            name = f"{name + 1}&"
        return name

    def _call(self, *args):
        return ahk_call("Menu", self.name, *args)


def _bare_menu_item_handler(callback, *_):
    callback()


def _menu_item_handler(callback, item_name, item_pos, menu_name):
    callback(item_name=item_name, item_pos=item_pos-1, menu=Menu(menu_name))


class TrayMenu(Menu):
    """The tray menu object.

    Can be used to change items in the tray menu and the appearence of the
    application in the notification area.

    Example usage::

        ahkpy.tray_menu.hide_tray_icon()
        ahkpy.tray_menu.show_tray_icon()
        ahkpy.tray_menu.set_clicks(1)

        ahkpy.hotkey("F1", ahkpy.tray_menu.toggle_tray_icon)

        ahkpy.tray_menu.delete_all_items()
        ahkpy.tray_menu.add("E&xit", sys.exit, default=True)
    """

    __slots__ = ("name",)

    def __init__(self):
        super().__init__("tray")

    @property
    def tray_icon_file(self):
        """The current tray icon file name.

        Returns ``None`` if the icon hasn't been changed.

        Setting a new file name resets the icon number to 0.

        :type: str

        :variable: `A_IconFile
           <https://www.autohotkey.com/docs/Variables.htm#IconFile>`_
        :command: `Menu, Tray, Icon, FileName, 0
           <https://www.autohotkey.com/docs/commands/Menu.htm#TrayIcon>`_
        """
        return ahk_call("GetVar", "A_IconFile") or None

    @tray_icon_file.setter
    def tray_icon_file(self, filename):
        self.set_tray_icon(filename)

    @property
    def tray_icon_number(self):
        """The current tray icon number in an icon group.

        Returns ``None`` if the icon hasn't been changed.

        :type: int

        :variable: `A_IconNumber
           <https://www.autohotkey.com/docs/Variables.htm#IconNumber>`_
        :command: `Menu, Tray, Icon, %A_IconFile%, Number
           <https://www.autohotkey.com/docs/commands/Menu.htm#TrayIcon>`_
        """
        number = ahk_call("GetVar", "A_IconNumber")
        if isinstance(number, int):
            return number - 1
        # Default icon, no number.
        return None

    @tray_icon_number.setter
    def tray_icon_number(self, number):
        filename = self.tray_icon_file
        if filename:
            self.set_tray_icon(filename, number=number)

    def set_tray_icon(self, filename=UNSET, *, number=None, affected_by_suspend=None):
        """Change the script's tray icon.

        The *filename* argument can be either an icon file (ICO, CUR, ANI, EXE,
        DLL, CPL, SCR) or any image in a format supported by AutoHotkey.

        To restore the default tray icon, pass ``None`` to *filename*.

        The optional *number* argument sets the icon group to use. It defaults
        to 0, which is the first group in the file. If *number* is negative, its
        absolute value is assumed to be the resource ID of an icon within an
        executable file.

        If the optional *affected_by_suspend* argument is true (default),
        enabling Suspended mode via :func:`suspend` or via the tray menu changes
        the icon.

        :command: `Menu, Tray, Icon, FileName, IconNumber
           <https://www.autohotkey.com/docs/commands/Menu.htm#TrayIcon>`_
        """
        if filename is None:
            # Set default icon.
            self.set_tray_icon("*")
            return
        if isinstance(number, int):
            number += 1
        if affected_by_suspend:
            freeze = "0"
        elif affected_by_suspend is not None:
            freeze = "1"
        else:
            freeze = None
        self._call("Icon", filename or "", number, freeze)

    @property
    def is_tray_icon_visible(self):
        """Whether the icon is visible in the notification area.

        :type: bool

        :variable: `A_IconHidden
           <https://www.autohotkey.com/docs/Variables.htm#IconHidden>`_
        :command: `Menu, Tray, Icon
           <https://www.autohotkey.com/docs/Variables.htm#Icon>`_
        """
        return not ahk_call("GetVar", "A_IconHidden")

    @is_tray_icon_visible.setter
    def is_tray_icon_visible(self, is_tray_icon_visible):
        if is_tray_icon_visible:
            self.show_tray_icon()
        else:
            self.hide_tray_icon()

    def toggle_tray_icon(self):
        """Toggle the icon visibility in the notification area."""
        self.is_tray_icon_visible = not self.is_tray_icon_visible

    def show_tray_icon(self):
        """Show the icon in the notification area."""
        self._call("Icon")

    def hide_tray_icon(self):
        """Hide the icon from the notification area."""
        self._call("NoIcon")

    @property
    def tip(self):
        """The tray icon's tooltip text.

        To restore the default text, set the property to ``None``.

        :variable: `A_IconTip
           <https://www.autohotkey.com/docs/Variables.htm#IconTip>`_
        :command: `Menu, Tray, Tip
           <https://www.autohotkey.com/docs/Variables.htm#Icon>`_
        """
        return ahk_call("GetVar", "A_IconTip") or None

    @tip.setter
    def tip(self, text):
        self._call("Tip", text)

    def set_clicks(self, number):
        """Set the number of clicks to activate the tray menu's default menu
        item.

        Defaults to 2 clicks.
        """
        self._call("Click", number)


tray_menu = TrayMenu()
