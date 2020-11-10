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

.. autoclass:: MessageBox(text=None, title=None, buttons="ok", icon=None, default_button=1, options=[], timeout=None)

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

   By default, the function waits indefinitely and returns ``True`` when the
   user presses the key. The optional *timeout* argument specifies the number
   of seconds to wait before returning ``False`` if there was no input.

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


Timers
------

.. autofunction:: set_timer

.. autofunction:: set_countdown

.. autoclass:: Timer
   :members:
