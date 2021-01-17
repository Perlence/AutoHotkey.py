API Reference
=============

.. module:: ahkpy

This part of the documentation covers all the interfaces of AutoHotkey.py. For
parts where AutoHotkey.py depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Clipboard
---------

.. TODO: Add short introductions to each section.

This section describes functions that work with the Windows clipboard.

.. autofunction:: get_clipboard

.. autofunction:: set_clipboard

.. autofunction:: wait_clipboard

.. autofunction:: on_clipboard_change

.. autoclass:: ClipboardHandler
   :members:


Exception
---------

.. autoexception:: Error
   :members:


Flow
----

.. autofunction:: sleep

.. autofunction:: poll

.. autofunction:: suspend

.. autofunction:: resume

.. autofunction:: toggle_suspend

.. autofunction:: restart

.. autofunction:: output_debug

.. autofunction:: coop

.. autofunction:: ahkpy.flow.ahk_call


GUI
---

Menus
~~~~~

.. autoclass:: Menu
   :members:

.. data:: tray_menu

   The default instance of :class:`TrayMenu`.

.. autoclass:: TrayMenu
   :show-inheritance:
   :members:

Message Boxes
~~~~~~~~~~~~~

.. autofunction:: message_box

.. autoclass:: MessageBox
   :members:

Tooltips
~~~~~~~~

.. autoclass:: ToolTip
   :members:

Window Messages
~~~~~~~~~~~~~~~

.. autofunction:: on_message

.. autoclass:: MessageHandler
   :members:


Keyboard and Mouse
------------------

Hotkeys and Hotstrings
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ahkpy.HotkeyContext
   :members:

.. data:: default_context

   The default instance of :class:`HotkeyContext`.

.. function:: hotkey(...)
.. function:: hotstring(...)
.. function:: remap_key(...)

   Useful aliases for :meth:`default_context.hotkey()
   <ahkpy.HotkeyContext.hotkey>`, :meth:`default_context.hotstring()
   <ahkpy.HotkeyContext.hotstring>`, and :meth:`default_context.remap_key()
   <ahkpy.HotkeyContext.remap_key>`.

.. autoclass:: Hotkey
   :members:

.. autoclass:: RemappedKey
   :members:

.. autoclass:: Hotstring
   :members:

.. autofunction:: reset_hotstring

.. autofunction:: get_hotstring_end_chars

.. autofunction:: set_hotstring_end_chars

.. autofunction:: get_hotstring_mouse_reset

.. autofunction:: set_hotstring_mouse_reset

Sending
~~~~~~~

.. autofunction:: send

.. function:: send_event(keys, **options)
.. function:: send_input(keys, **options)
.. function:: send_play(keys, **options)

   Send simulated keystrokes and mouse clicks using the corresponding mode.

   For arguments refer to :func:`send`.

Mouse
~~~~~

.. autofunction:: click
.. autofunction:: mouse_press
.. autofunction:: mouse_release
.. autofunction:: right_click
.. autofunction:: double_click
.. autofunction:: mouse_scroll
.. autofunction:: mouse_move

The `MouseClickDrag
<https://www.autohotkey.com/docs/commands/MouseClickDrag.htm>`_ command can be
implemented as follows::

   ahkpy.mouse_move(x=x1, y=y1)
   ahkpy.mouse_press(which_button)
   ahkpy.mouse_move(x=x2, y=y2, speed=speed, relative_to=...)
   ahkpy.mouse_release()

.. autofunction:: get_mouse_pos
.. autofunction:: get_window_under_mouse
.. autofunction:: get_control_under_mouse

.. autofunction:: get_cursor_type

Key States
~~~~~~~~~~

In the following functions, the *key_name* argument is a VK or SC code, such as
``"vkA2"`` or ``"sc01D"``, a combination of both, or a key from the `key list
<https://www.autohotkey.com/docs/KeyList.htm>`_.

.. autofunction:: get_key_name

.. autofunction:: get_key_name_from_vk

.. autofunction:: get_key_name_from_sc

.. autofunction:: get_key_vk

.. autofunction:: get_key_sc

.. autofunction:: is_key_pressed

.. autofunction:: is_key_pressed_logical

.. function:: wait_key_pressed(key_name, timeout: float = None) -> bool
.. function:: wait_key_released(key_name, timeout: float = None) -> bool
.. function:: wait_key_pressed_logical(key_name, timeout: float = None) -> bool
.. function:: wait_key_released_logical(key_name, timeout: float = None) -> bool

   Wait for a key or mouse/joystick button to be pressed/released
   physically/logically.

   Returns ``True`` when the user presses the key. If there is no user input
   after *timeout* seconds, then ``False`` will be returned. If *timeout* is
   not specified or ``None``, there is no limit to the wait time.

   The logical state is the state that the OS and the active window believe the
   key to be in, but is not necessarily the same as the physical state, that is,
   whether the user is physically holding it down.

   :command: `KeyWait <https://www.autohotkey.com/docs/commands/KeyWait.htm>`_

.. function:: get_caps_lock_state() -> bool
.. function:: get_num_lock_state() -> bool
.. function:: get_scroll_lock_state() -> bool
.. function:: get_insert_state() -> bool

   Retrieve the toggle state of :kbd:`CapsLock`, :kbd:`NumLock`,
   :kbd:`ScrollLock`, and :kbd:`Insert` keys.

   :command: `GetKeyState
      <https://www.autohotkey.com/docs/commands/GetKeyState.htm>`_

.. function:: set_caps_lock_state(state: bool, always=False)
.. function:: set_num_lock_state(state: bool, always=False)
.. function:: set_scroll_lock_state(state: bool, always=False)

   Set the toggle state of :kbd:`CapsLock`, :kbd:`NumLock`, and
   :kbd:`ScrollLock` keys.

   If the optional *always* argument is True, forces the key to stay on or off.

   :command: `SetCapsLockState / SetNumLockState / SetScrollLockState
      <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_

Input Blocking
~~~~~~~~~~~~~~

A couple of context managers to block user input::

   with ahkpy.block_input():
       subprocess.Popen(["notepad"])
       ahkpy.windows.wait_active("Untitled - Notepad")
       ahkpy.send("{F5}")  # Pastes time and date

Use sparingly. Prefer the Input and Play send modes instead, because they buffer
the user input while sending.

.. autofunction:: block_input

.. autofunction:: block_input_while_sending

.. autofunction:: block_mouse_move


Settings
--------

Settings modify the delay between execution of :class:`Window` and
:class:`Control` methods; set the mode, level, delay and duration of the
simulated key presses and mouse clicks, the speed of mouse movement.

Each thread has its own current settings which are accessed or changed using the
:func:`get_settings` and :func:`set_settings` functions.

.. autofunction:: get_settings

.. autofunction:: set_settings

.. autofunction:: local_settings

.. data:: default_settings

   The default instance of :class:`Settings`. It is set as the current settings
   at the start of the program. Changing individual settings here affects all
   yet-to-be-run AHK callbacks and Python threads.

.. autoclass:: Settings
   :members:


Timers
------

.. autofunction:: set_timer

.. autofunction:: set_countdown

.. autoclass:: Timer
   :members:


Windows
-------

.. data:: windows
.. data:: visible_windows

   The instances of :class:`Windows` that match only visible windows.

.. data:: all_windows

   An instance of :class:`Windows` that matches visible and hidden windows.

   The following example shows how to get the window ID of the main AutoHotkey
   window::

      import os
      ahk_win = ahk.all_windows.first(pid=os.getpid())

.. autoclass:: Windows
   :members:
   :special-members: __iter__, __len__
   :exclude-members: exist, top, bottom

.. autoclass:: ahkpy.window.WindowHandle
   :members:
   :special-members: __bool__

.. autoclass:: ahkpy.window.BaseWindow
   :show-inheritance:
   :members:
   :exclude-members: exe

.. autoclass:: Window
   :show-inheritance:
   :members:
   :exclude-members: enable, disable, show, hide

.. autoclass:: Control
   :show-inheritance:
   :members:
   :exclude-members: enable, disable, show, hide

.. autoclass:: WindowStyle
   :show-inheritance:
   :members:

.. autoclass:: ExWindowStyle
   :show-inheritance:
   :members:
