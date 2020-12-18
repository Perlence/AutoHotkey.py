Quickstart
==========

.. module:: ahkpy

This page assumes you already have AutoHotkey.py installed. If you do not, head
over to the :doc:`/install` section. If you need a refresher on Python, check
out `The Python Tutorial <https://docs.python.org/3/tutorial/index.html>`_.


Command Line Interface
----------------------

When invoking AutoHotkey.py, you may specify any of these options:

.. code-block:: text

   ahkpy [-h] [-q] [--no-tray] [-c CMD | -m MOD | FILE | -] [args]

The most common use case is, of course, a simple invocation of a script:

.. code-block:: text

   ahkpy myscript.py

The AutoHotkey.py interface resembles that of the Python interpreter. For more
information on the interface options refer to `Python documentation
<https://docs.python.org/3/using/cmdline.html#interface-options>`_.

The following CLI options are specific to AutoHotkey.py:

.. cmdoption:: -q

   Suppress message boxes with errors. If this option is not specified,
   AutoHotkey.py will show unhandled Python errors in message boxes.

.. cmdoption:: --no-tray

   Don't show the AutoHotkey icon in the system tray.

.. note::

   In contrast with AutoHotkey, the whole script is executed once it's loaded.
   That is, there are no separate `auto-execute
   <https://www.autohotkey.com/docs/Language.htm#auto-execute-section>`_ and
   hotkey/hotstring sections. Hotkeys are registered as the script is executed
   line by line.


Hotkeys
-------

Hotkeys in AutoHotkey.py are registered with the :func:`hotkey` function. In the
following example, the hotkey :kbd:`Win+N` is configured to launch Notepad. The
pound sign ``#`` stands for the :kbd:`Win` key, which is known as a modifier::

   import subprocess
   import ahkpy

   @ahkpy.hotkey("#n"):
   def run_notepad():
       subprocess.Popen(["notepad"])

If you want to bind an existing function to a hotkey, pass it as an argument to
:func:`hotkey`::

   ahkpy.hotkey("#n", subprocess.Popen, ["notepad"])

In the example above, the :class:`subprocess.Popen` class will be created with
the ``["notepad"]`` argument when the user presses :kbd:`Win+N`.

A key or key-combination can be disabled for the entire system by having it do
nothing. The following example disables the right-side Win key::

   ahkpy.hotkey("RWin", lambda: None)

The functions :meth:`Windows.active_window_context`,
:meth:`Windows.window_context` and :class:`HotkeyContext` can be used to make a
hotkey perform a different action (or none at all) depending on a specific
condition. For example::

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

   def is_mouse_over_taskbar():
       win = ahkpy.get_window_under_mouse()
       return win.class_name == "Shell_TrayWnd"

   # Wheel over taskbar: increase/decrease volume.
   taskbar_ctx = ahkpy.HotkeyContext(is_mouse_over_taskbar)
   taskbar_ctx.hotkey("WheelUp", ahkpy.send, "{Volume_Up}")
   taskbar_ctx.hotkey("WheelDown", ahkpy.send, "{Volume_Down}")


Settings
--------

.. TODO: The following text is a bit convoluted.

Every time a callable is passed to AutoHotkey as a callback, e.g. in
:func:`hotkey`, :func:`set_timer()`, etc, the callback takes a snapshot of
the current context using the :func:`contextvars.copy_context` function. This
snapshot contains a *reference* to the current :class:`Settings` object. When
the callback is executed, it uses this reference to access the settings. This
means, for example, that you can change the settings after the hotkey was
created, and the hotkey callback will be aware of that change::

   ahkpy.default_settings.win_delay = 0.1

   # The callback stores only the reference to
   # ahkpy.default_settings, not the actual settings values.
   ahkpy.hotkey("F1", lambda: print(ahkpy.get_settings().win_delay))

   @ahkpy.hotkey("F2")
   def change_defaults():
       ahkpy.default_settings.win_delay = 0.2
       assert ahkpy.get_settings() is ahkpy.default_settings

If you press :kbd:`F1`, you will see ``0.1`` printed. Press :kbd:`F2` and
then :kbd:`F1` and you will see ``0.2`` printed.

This also means that the settings that the :kbd:`F2` hotkey callback has is
the same exact settings object that the :kbd:`F1` hotkey has. If you want to
change the settings only in one callback, use the :func:`local_settings`
function.


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
AutoHotkey.py program as you would do with a regular Python program.
