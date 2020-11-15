API
===

.. module:: ahkpy

This part of the documentation covers all the interfaces of AutoHotkey.py. For
parts where AutoHotkey.py depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Clipboard
---------

.. TODO: Add short introductions to each section.

.. autofunction:: get_clipboard

.. autofunction:: set_clipboard

.. autofunction:: wait_clipboard

.. autofunction:: on_clipboard_change

.. autoclass:: ClipboardHandler
   :members:


Flow
----

.. autofunction:: sleep

.. autofunction:: suspend

.. autofunction:: resume

.. autofunction:: toggle_suspend

.. autofunction:: reload

.. autofunction:: output_debug

.. autofunction:: coop

.. autofunction:: ahkpy.flow.ahk_call


GUI
---

Message Boxes
~~~~~~~~~~~~~

.. autofunction:: message_box

.. autoclass:: MessageBox

   .. automethod:: show
   .. automethod:: info
   .. automethod:: warning
   .. automethod:: error
   .. automethod:: ok_cancel
   .. automethod:: yes_no
   .. automethod:: yes_no_cancel
   .. automethod:: retry_cancel
   .. automethod:: cancel_try_continue

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
<https://www.autohotkey.com/docs/commands/MouseClickDrag.htm>`__ command can be
implemented as follows::

   ahkpy.mouse_move(x=x1, y=y1)
   ahkpy.mouse_press(which_button)
   ahkpy.mouse_move(x=x2, y=y2, speed=speed, relative_to=...)
   ahkpy.mouse_release()

.. autofunction:: get_mouse_pos
.. autofunction:: get_window_under_mouse
.. autofunction:: get_control_under_mouse

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

   AutoHotkey command: `KeyWait
   <https://www.autohotkey.com/docs/commands/KeyWait.htm>`_.

.. function:: get_caps_lock_state() -> bool
.. function:: get_num_lock_state() -> bool
.. function:: get_scroll_lock_state() -> bool
.. function:: get_insert_state() -> bool

   Retrieve the toggle state of :kbd:`CapsLock`, :kbd:`NumLock`,
   :kbd:`ScrollLock`, and :kbd:`Insert` keys.

   AutoHotkey function: `GetKeyState
   <https://www.autohotkey.com/docs/commands/GetKeyState.htm>`_.

.. function:: set_caps_lock_state(state: bool, always=False)
.. function:: set_num_lock_state(state: bool, always=False)
.. function:: set_scroll_lock_state(state: bool, always=False)

   Set the toggle state of :kbd:`CapsLock`, :kbd:`NumLock`, and
   :kbd:`ScrollLock` keys.

   If the optional *always* argument is True, forces the key to stay on or off.

   AutoHotkey command: `SetCapsLockState / SetNumLockState / SetScrollLockState
   <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_.


Input Blocking
~~~~~~~~~~~~~~

A couple of context managers to block user input.

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

.. note::

   .. TODO: The following text is a bit hard to understand.

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

   An instance of :class:`Windows` that matches only visible windows.

.. data:: all_windows

   An instance of :class:`Windows` that matches visible and hidden windows.

.. autoclass:: Windows
   :members:
   :exclude-members: first, top, bottom
   :special-members: __iter__, __len__

.. autoclass:: Window
   :members:

.. autoclass:: Control
   :members:

.. autoclass:: WindowStyle
   :members:

.. autoclass:: ExWindowStyle
   :members:
