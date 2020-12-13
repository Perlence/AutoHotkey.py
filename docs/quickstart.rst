Quickstart
==========

.. module:: ahkpy

Settings
--------

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

Debugging
---------
