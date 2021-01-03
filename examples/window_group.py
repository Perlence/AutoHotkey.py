"""Manage window groups.

When two or more windows are grouped it means that when one of them gets
activated, the others are brought to the front. For example, you can group an
editor window and a documentation window. Next time you activate the editor
window, the documentation window is brought up so you can see both windows.
Conversely, when you activate the documentation window, the editor is brought
up.

To add window to the group, activate it and press Apps+G. To remove the window
from the group, activate it and press Apps+G again. When the window is closed,
it's automatically removed from the group. If after removing the window there's
only one window left in the group, the group is dissolved.
"""

import os
from ctypes import windll

import ahkpy as ahk


HSHELL_WINDOWDESTROYED = 0x0002
HSHELL_WINDOWACTIVATED = 0x0004
HSHELL_RUDEAPPACTIVATED = 0x8004

window_group = set()
previous_win = None

ahk_win = ahk.all_windows.first(pid=os.getpid())
windll.user32.RegisterShellHookWindow(ahk_win.id)
msgnum = windll.user32.RegisterWindowMessageW("SHELLHOOK")


@ahk.on_message(msgnum)
def handle_shell_message(w_param, l_param, **kw):
    win_id = l_param
    win = ahk.Window(win_id)
    if w_param == HSHELL_WINDOWDESTROYED:
        remove_window_from_group(win)
    elif w_param in (HSHELL_WINDOWACTIVATED, HSHELL_RUDEAPPACTIVATED):
        on_window_activated(win)


@ahk.hotkey("AppsKey & g")
def toggle_window_in_group():
    active_win = ahk.windows.get_active()
    if active_win in window_group:
        remove_window_from_group(active_win)
    else:
        window_group.add(active_win)


def on_window_activated(win):
    global previous_win

    if not win:
        remove_window_from_group(win)
        return

    if win in window_group:
        for grouped_win in window_group:
            if grouped_win == win:
                continue
            if previous_win and previous_win == grouped_win:
                continue
            grouped_win.toggle_always_on_top()
            grouped_win.toggle_always_on_top()
        win.toggle_always_on_top()
        win.toggle_always_on_top()

    previous_win = win


def remove_window_from_group(win):
    if win in window_group:
        window_group.remove(win)
        if len(window_group) == 1:
            window_group.clear()
