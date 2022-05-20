Quickstart
==========

.. module:: ahkpy
   :noindex:

This page assumes you've already installed AutoHotkey.py. If you haven't, head
over to the :doc:`/install` section. If you need a refresher on Python, check
out `The Python Tutorial <https://docs.python.org/3/tutorial/index.html>`_.


Command Line Interface
----------------------

When invoking AutoHotkey.py, you may specify any of these options:

.. code-block:: text

   ahkpy [-h] [-V] [-q] [--no-tray] [-c CMD | -m MOD | FILE | -] [args]

The most common use case, of course, simply invokes a script:

.. code-block:: text

   ahkpy myscript.py

The REPL interface works best when you invoke it with the ``python`` executable,
which allows you to explore your command history with the up and down arrow
keys.

.. code-block:: text

   python -m ahkpy

To start AutoHotkey.py without the terminal window, use *pyw*:

.. code-block:: text

   pyw -m ahkpy myscript.py

The AutoHotkey.py interface resembles that of the Python interpreter. To learn
more about your interface options, refer to the `Python documentation
<https://docs.python.org/3/using/cmdline.html#interface-options>`_.

The following CLI options are specific to AutoHotkey.py:

.. cmdoption:: -q

   Suppress message boxes with errors. If you don't specify this option,
   AutoHotkey.py shows unhandled Python errors in message boxes.

.. cmdoption:: --no-tray

   Don't show the AutoHotkey icon in the system tray.

Once started, AutoHotkey.py searches for the AutoHotkey executable in the
following sequence:

1. First, checks whether the ``AUTOHOTKEY`` environment variable is set. If it
   is, AutoHotkey.py uses the environment variable as the AutoHotkey executable
   path.
2. If not, checks the Windows Registry to find whether a program's set to run
   when a user opens an AHK file. If the program name starts with ``autohotkey``
   (case-insensitive), AutoHotkey.py uses it as the AutoHotkey executable path.
3. Otherwise, defaults to the path
   ``C:\Program Files\AutoHotkey\AutoHotkey.exe``.

.. note::

   In contrast with AutoHotkey, the whole script is executed once it's loaded.
   That is, there are no separate `auto-execute
   <https://www.autohotkey.com/docs/Language.htm#auto-execute-section>`_ and
   hotkey/hotstring sections. Hotkeys are registered as the script is executed
   line by line.


Hotkeys
-------

The :func:`hotkey` function registers Hotkeys. In the following example, the
hotkey :kbd:`Win` + :kbd:`N` is configured to launch Notepad. The pound sign
``#`` stands for the :kbd:`Win` key, one of the hotkey modifiers::

   import subprocess
   import ahkpy

   @ahkpy.hotkey("#n")
   def run_notepad():
       subprocess.Popen(["notepad"])

If you want to bind an existing function to a hotkey, pass it as an argument to
:func:`hotkey`::

   ahkpy.hotkey("#n", subprocess.Popen, ["notepad"])

In the preceding example, when a user presses :kbd:`Win` + :kbd:`N`, they create
a :class:`subprocess.Popen` object with the argument ``["notepad"]``.

To disable a key or a combination of keys for the entire system, use the
``lambda: None`` function. For example, this disables the right-side :kbd:`Win`
key::

   ahkpy.hotkey("RWin", lambda: None)

If you want to specify certain conditions when a hotkey performs a different
action (or no action at all), you can use the methods
:meth:`Windows.active_window_context` and :meth:`Windows.window_context`, or the
class :class:`HotkeyContext`. For example::

   notepad_ctx = ahkpy.windows.active_window_context(class_name="Notepad")
   notepad_ctx.hotkey(
       "^a", ahkpy.message_box,
       "You pressed Ctrl-A while Notepad is active. Pressing Ctrl-A in any "
       "other window will pass the Ctrl-A keystroke to that window.",
   )
   notepad_ctx.hotkey(
       "#c", ahkpy.message_box, "You pressed Win-C while Notepad is active.",
   )

   ctx = ahkpy.windows.active_window_context()
   ctx.hotkey(
       "#c", ahkpy.message_box,
       "You pressed Win-C while any window except Notepad is active.",
   )

.. code-block::

   def is_mouse_over_taskbar():
       win = ahkpy.get_window_under_mouse()
       return win.class_name == "Shell_TrayWnd"

   # Wheel over taskbar: increase/decrease volume.
   taskbar_ctx = ahkpy.HotkeyContext(is_mouse_over_taskbar)
   taskbar_ctx.hotkey("WheelUp", ahkpy.send, "{Volume_Up}")
   taskbar_ctx.hotkey("WheelDown", ahkpy.send, "{Volume_Down}")

The same handler can be assigned to multiple hotkeys::

   import os
   import re
   import subprocess

   import ahkpy

   def open_explorer(mode):
       """
       Ctrl+Shift+O to open containing folder in Explorer.
       Ctrl+Shift+E to open folder with current file selected.
       Supports SciTE and Notepad++.
       """
       path = ahkpy.windows.get_active().title
       if not path:
           return

       mo = re.match(r"\*?((.*)\\[^\\]+)(?= [-*] )", path)
       if not mo:
           return

       file = mo.group(1)
       folder = mo.group(2)
       if mode == "folder" and os.path.exists(folder):
           subprocess.Popen(["explorer.exe", f'/select,"{folder}"')
       else:
           subprocess.Popen(["explorer.exe", f'"{file}"')

   ahkpy.hotkey("^+o", open_explorer, "file")
   ahkpy.hotkey("^+e", open_explorer, "folder")

For more examples see the original `Hotkeys
<https://www.autohotkey.com/docs/Hotkeys.htm>`_ usage.


Window Management
-----------------

AutoHotkey.py provides the :class:`Windows` class and its default instances:
:data:`windows` and :data:`all_windows`. With the :class:`Windows` class, you
can query windows through multiple search parameters, like title and window
class. To query the windows, set the criteria with the :meth:`~Windows.filter`
method. For example, this prepares a query of all windows of the class
``ConsoleWindowClass``::

   >>> console_windows = ahkpy.windows.filter(class_name="ConsoleWindowClass")

The only role of the :meth:`~Windows.filter` method is to pack the query
parameters. Once you've set the filters you want, you can perform a real
operation, like get the count of matching windows::

   >>> console_windows
   Windows(class_name='ConsoleWindowClass', hidden_windows=False, hidden_text=True, title_mode='startswith', text_mode='fast')
   >>> len(console_windows)  # Check how many console windows there are now.
   3
   >>> if console_windows:
   ...     print("yes")  # Executed if there's at least one console window.
   ...
   yes
   >>> list(console_windows)  # Retrieve the list of window instances.
   [Window(id=39784856), Window(id=29757762), Window(id=262780)]
   >>> [win.title for win in console_windows]
   ['Command Prompt', 'Windows PowerShell', 'C:\\Windows\\py.exe']

Specifying multiple criteria for :meth:`~Windows.filter` narrows the search down
to only the windows where *all* criteria match. In the following example, the
script waits for a window whose title contains ``My File.txt`` and whose class
is ``Notepad``::

   ahkpy.windows.filter("My File.txt", class_name="Notepad").wait()
   # Filter chaining gives the same result.
   ahkpy.windows.filter("My File.txt").filter(class_name="Notepad").wait()

Calling :meth:`~Windows.filter` is useful when you want to create and reuse a
selection of windows. However, all :class:`Windows` methods receive the search
criteria, so the :meth:`~Windows.wait` example above can be shortened to the
following::

   ahkpy.windows.wait("My File.txt", class_name="Notepad")

The :meth:`~Windows.exclude` method is a companion to :meth:`~Windows.filter`
that excludes a window from a search::

   non_cmd_windows = ahkpy.windows.exclude(title="Command Prompt")

For more fine-grained window filtering, use list comprehensions::

   >>> # Get all tool windows of paint.net.
   >>> [
   ...     win.title
   ...     for win in ahkpy.windows.filter(exe="PaintDotNet.exe")
   ...     if ahkpy.ExWindowStyle.TOOLWINDOW in win.ex_style
   ... ]
   ['Colors', 'Layers', 'History', 'Tools']

To get the currently active window, use the :meth:`~Windows.get_active` method::

   # Press Win+↑ to maximize the active window.
   ahkpy.hotkey("#Up", lambda: ahkpy.windows.get_active().maximize())

To get first (top-most) window from a query, use the :meth:`~Windows.first`
method::

   >>> ahkpy.windows.first(class_name="Notepad")
   Window(id=6426410)

The :meth:`~Windows.first`, :meth:`~Windows.last`, :meth:`~Windows.get_active`,
:meth:`~Windows.wait` methods return a :class:`Window` instance. If there are no
matching windows, ``Window(None)`` is returned. This object is falsy and returns
``None`` for most of its properties::

   >>> win = ahkpy.windows.first(class_name="there's no such window")
   >>> win
   Window(id=None)
   >>> win.exists
   False
   >>> if win:
   ...     print("window exists")  # Will not be printed.
   ...
   >>> win.is_visible
   False
   >>> win.show()  # Does nothing.
   >>> win.class_name is None
   True

Also, if a window existed at some point in time but was closed, it acts the same
as ``Window(None)``. Thus, be sure to check property values for ``None`` before
working with them::

   >>> win = ahkpy.windows.first(class_name="Notepad")
   >>> win
   Window(id=6819626)
   >>> win.close()
   >>> win.exists
   False
   >>> bool(win)
   False
   >>> win.class_name is None
   True


DLL Calls
---------

Use :mod:`ctypes` to call DLL functions::

   >>> from ctypes import windll
   >>> windll.user32.MessageBoxW(0, "Press Yes or No", "Title of box", 4)
   6

Structure example `#11
<https://www.autohotkey.com/docs/commands/DllCall.htm#ExStruct>`_::

   >>> import subprocess
   >>> from ctypes import byref, windll
   >>> from ctypes.wintypes import RECT
   >>>
   >>> subprocess.Popen(["notepad"])
   >>> notepad = ahkpy.windows.wait("Untitled - Notepad")
   >>> rect = RECT()
   >>> windll.user32.GetWindowRect(notepad.id, byref(rect))
   1
   >>> (rect.left, rect.top, rect.right, rect.bottom)
   (1063, 145, 1667, 824)

Structure example `#12
<https://www.autohotkey.com/docs/commands/DllCall.htm#ExStructRect>`_::

   >>> from ctypes import byref, windll
   >>> from ctypes.wintypes import HANDLE, RECT
   >>>
   >>> screen_width = windll.user32.GetSystemMetrics(0)
   >>> screen_height = windll.user32.GetSystemMetrics(1)
   >>> rect = RECT(0, 0, screen_width//2, screen_height//2)
   >>> # Pass zero to get the desktop's device context.
   >>> dc = windll.user32.GetDC(0)
   >>> # Create a red brush (0x0000FF is in BGR format).
   >>> brush = windll.gdi32.CreateSolidBrush(0x0000FF)
   >>> # Fill the specified rectangle using the brush above.
   >>> windll.user32.FillRect(dc, byref(rect), brush)
   >>> windll.gdi32.DeleteObject(brush)  # Clean-up.
   >>> windll.user32.ReleaseDC(0, HANDLE(dc))  # Clean-up.


Settings
--------

A *callback* is a function called by `timer </api.html#ahkpy.set_timer>`_,
`window message <api.html#ahkpy.on_message>`_, by `changing clipboard
<api.html#ahkpy.on_clipboard_change>`_, or by triggering a `hotkey
<api.html#ahkpy.HotkeyContext.hotkey>`_ or a `hotstring
<api.html#ahkpy.HotkeyContext.hotstring>`_.

In the original AutoHotkey, a hotkey callback executes with the *copy* of the
global settings. In contrast, in AutoHotkey.py, the callback gets a *reference*
to the current :class:`Settings` object, set by the :func:`set_settings` call.
Meaning that, changing the individual settings in the Python callback changes
them everywhere. Sometimes, you'll want to avoid doing so, in which case you
should use the :func:`local_settings` function. Other times, the implementation
will come in handy, like when you want to create a hotkey that changes the
global AHK settings::

   ahkpy.default_settings.win_delay = 0.1

   # The callback stores only the reference to
   # ahkpy.default_settings, not the actual settings values.
   ahkpy.hotkey("F1", lambda: print(ahkpy.get_settings().win_delay))

   @ahkpy.hotkey("F2")
   def change_defaults():
       ahkpy.default_settings.win_delay = 0.2
       assert ahkpy.get_settings() is ahkpy.default_settings

If you press :kbd:`F1`, you will see ``0.1`` printed, which is the current
:attr:`~Settings.win_delay`. Press :kbd:`F2` and then :kbd:`F1` and you will see
``0.2`` printed. Also, the settings object that the :kbd:`F2` hotkey callback
gets with the :func:`get_settings` call is the same exact settings object that
the :kbd:`F1` hotkey gets.


Debugging
---------

AutoHotkey.py supports :mod:`pdb`, the built-in Python debugger. Just put the
:func:`breakpoint` invocation in your code where you want to enter the debugger
and run the program. It works both during the main section and in the
callbacks::

   x = 0

   @ahkpy.hotkey("F1")
   def cb():
       global x
       x += 1
       breakpoint()  # Breakpoint in a callback

   breakpoint()  # Breakpoint in the main section

The Visual Studio Code debugger can be configured to work with AutoHotkey.py.
Follow the `Python debug configurations in Visual Studio Code
<https://code.visualstudio.com/docs/python/debugging>`_ guide to create your
``launch.json``. Once created, change the Python interpreter in the
``launch.json`` to ``ahkpy.exe``, for example:

.. code-block:: javascript

   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Current File",
               "type": "python",
               "request": "launch",
               "program": "${file}",
               "console": "integratedTerminal",
               // Add the following settings:
               "python": "ahkpy.exe",
               "pythonArgs": ["--no-tray"]
           }
       ]
   }

Now you can set the breakpoints in Visual Studio Code and inspect the
AutoHotkey.py program, as you would with a regular Python program.
