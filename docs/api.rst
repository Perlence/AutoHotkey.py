API
===

.. module:: ahkpy

This part of the documentation covers all the interfaces of AutoHotkey.py. For
parts where AutoHotkey.py depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Clipboard
---------

.. autofunction:: get_clipboard

.. autofunction:: set_clipboard

.. autofunction:: wait_clipboard

.. autofunction:: on_clipboard_change

.. autoclass:: ClipboardHandler
    :members:


Timers
------

.. autofunction:: set_timer

.. autofunction:: set_countdown

.. autoclass:: Timer
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
    .. automethod:: info(text, title=None, *, buttons="ok", default_button=1, **attrs) -> Optional[str]
    .. automethod:: warning(text, title=None, *, buttons="ok", default_button=1, **attrs) -> Optional[str]
    .. automethod:: error(text, title=None, *, buttons="ok", default_button=1, **attrs) -> Optional[str]
    .. automethod:: ok_cancel(text, title=None, *, icon="info", default_button=1, **attrs) -> Optional[bool]
    .. automethod:: yes_no(text, title=None, *, icon="info", default_button=1, **attrs) -> Optional[bool]
    .. automethod:: yes_no_cancel(text, title=None, *, icon="info", default_button=1, **attrs) -> Optional[str]
    .. automethod:: retry_cancel(text, title=None, *, icon="warning", default_button=1, **attrs) -> Optional[bool]
    .. automethod:: cancel_try_continue(text, title=None, *, icon="warning", default_button=2, **attrs) -> Optional[str]

.. autoclass:: ToolTip
    :members:

.. autofunction:: on_message

.. autoclass:: MessageHandler
    :members:
