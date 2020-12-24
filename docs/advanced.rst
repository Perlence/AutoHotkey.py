Advanced Usage
==============

This document covers some of AutoHotkey.py more advanced features.


Threading
---------

.. TODO: Background threads don't work unless the main is actively doing
   something.

If you need to wait for the background thread to finish, calling
:meth:`threading.Thread.join` in the main thread will block the handling of the
AHK message queue. That is, AHK won't be able to handle the hotkeys and other
callbacks. Let AHK handle its message queue by calling :func:`ahkpy.sleep`
repeatedly while checking that the background thread is alive::

   import threading
   th = threading.Thread(target=some_worker)
   th.start()
   while th.is_alive():
       ahkpy.sleep(0.01)

Calling blocking AHK functions from the background thread deadlocks the
program::

   def bg_thread():
       ahk.wait_key_pressed("F1")
       # ^^ Blocks the thread until F1 is pressed
       print("F1 pressed")

   th = threading.Thread(target=bg_thread, daemon=True)
   th.start()
   while th.is_alive():
       ahk.sleep(0.01)

Instead, use their nonblocking versions and yield control to other Python
threads with :func:`time.sleep`::

   def bg():
       while not ahk.is_key_pressed("F1"):
           time.sleep(0)
       print("F1 pressed")


GUI
---

.. TODO: Explain why AutoHotkey GUI is out of scope of this project and point to
   tkinter.
