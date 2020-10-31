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
