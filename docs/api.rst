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

.. autoclass:: ToolTip
   :members:

.. autofunction:: on_message

.. autoclass:: MessageHandler
   :members:


Keyboard and Mouse
------------------

Hotkeys and Hotstrings
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ahkpy.hotkey_context.BaseHotkeyContext
   :members:

.. data:: default_context

   The default instance of :class:`ahkpy.hotkey_context.BaseHotkeyContext`.

.. function:: hotkey(...)
.. function:: hotstring(...)
.. function:: remap_key(...)

   Useful aliases for :meth:`default_context.hotkey()
   <ahkpy.hotkey_context.BaseHotkeyContext.hotkey>`,
   :meth:`default_context.remap_key()
   <ahkpy.hotkey_context.BaseHotkeyContext.remap_key>`, and
   :meth:`default_context.hotstring()
   <ahkpy.hotkey_context.BaseHotkeyContext.hotstring>`.

.. autoclass:: HotkeyContext
   :show-inheritance:
   :members:

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

.. autofunction:: send_event

.. autofunction:: send_input

.. autofunction:: send_play

Key States
~~~~~~~~~~

.. autofunction:: get_key_name

.. autofunction:: get_key_sc

.. autofunction:: get_key_vk

.. autofunction:: is_key_pressed

.. autofunction:: is_key_pressed_logical

.. autofunction:: wait_key_pressed

.. autofunction:: wait_key_released

.. autofunction:: wait_key_pressed_logical

.. autofunction:: wait_key_released_logical

.. autofunction:: get_caps_lock_state

.. autofunction:: set_caps_lock_state

.. autofunction:: get_num_lock_state

.. autofunction:: set_num_lock_state

.. autofunction:: get_scroll_lock_state

.. autofunction:: set_scroll_lock_state

.. autofunction:: get_insert_state

Input Blocking
~~~~~~~~~~~~~~

A couple of context managers to block user input.

.. autofunction:: block_input_while_sending

.. autofunction:: block_input

.. autofunction:: block_mouse_move


Timers
------

.. autofunction:: set_timer

.. autofunction:: set_countdown

.. autoclass:: Timer
   :members:
