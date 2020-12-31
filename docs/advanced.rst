Advanced Usage
==============

This document covers some of AutoHotkey.py more advanced features.


Threading
---------

In Python, the :mod:`threading` module can be used to improve the responsiveness
of applications that accept user input while other tasks run in the background.
A related use case is running I/O in parallel with computations in another
thread. These are actual OS threads, as opposed to AHK `pseudo-threads
<https://www.autohotkey.com/docs/misc/Threads.htm>`_.

Calling AHK functions from Python is implemented in AutoHotkey.py by registering
a callback in AHK with `RegisterCallback
<https://www.autohotkey.com/docs/commands/RegisterCallback.htm>`_. *These
callbacks are not reentrant.* That is, while the *main thread* is busy executing
an AHK function, trying to call another AHK function from *another thread* leads
to unpredictable results like program crash.

Thus, a *Global AutoHotkey Lock* (GAL) was introduced. It ensures that only one
OS thread interacts with AHK at a time.

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


asyncio
-------

AutoHotkey.py works well with :mod:`asyncio`. When starting a long-running loop,
schedule the :func:`ahkpy.sleep` call repeatedly, so it could give time to AHK
to process its message queue (hotkeys, menu)::

   import asyncio

   import ahkpy

   async def main():
       # Schedule a function that will check AHK message queue repeatedly.
       loop = asyncio.get_running_loop()
       loop.call_soon(sleeper, loop)

       print('Hello ...')
       await asyncio.sleep(1)
       print('... World!')

   def sleeper(loop):
       ahkpy.sleep(0.01)
       loop.call_soon(sleeper, loop)

   asyncio.run(main())

Check out the `example of a TCP server
<https://github.com/Perlence/AutoHotkey.py/blob/master/examples/remote_send.py>`_
that receives *keys* strings and passes them to :func:`ahkpy.send`.


GUI
---

Out of the box, Python provides the :mod:`tkinter` package, an interface to the
Tk GUI toolkit. AutoHotkey.py supports :mod:`tkinter`, so it can be used to
create user interfaces.

The following table contains a list of AutoHotkey GUI controls and the
corresponding tkinter counterparts:

.. list-table::
   :header-rows: 1

   + - AHK Control
     - tkinter Widget
   + - `Text <https://www.autohotkey.com/docs/commands/GuiControls.htm#Text>`_
     - :class:`tkinter.ttk.Label`
   + - `Edit <https://www.autohotkey.com/docs/commands/GuiControls.htm#Edit>`_
     - :class:`tkinter.ttk.Entry`
   + - `UpDown <https://www.autohotkey.com/docs/commands/GuiControls.htm#UpDown>`_
     - :class:`tkinter.ttk.Spinbox`
   + - `Picture <https://www.autohotkey.com/docs/commands/GuiControls.htm#Picture>`_
     - :class:`tkinter.BitmapImage`, :class:`tkinter.PhotoImage`
   + - `Button <https://www.autohotkey.com/docs/commands/GuiControls.htm#Button>`_
     - :class:`tkinter.ttk.Button`
   + - `Checkbox <https://www.autohotkey.com/docs/commands/GuiControls.htm#Checkbox>`_
     - :class:`tkinter.ttk.Checkbutton`
   + - `Radio <https://www.autohotkey.com/docs/commands/GuiControls.htm#Radio>`_
     - :class:`tkinter.ttk.Radiobutton`
   + - `DropDownList <https://www.autohotkey.com/docs/commands/GuiControls.htm#DropDownList>`_
     - :class:`tkinter.ttk.Combobox`
   + - `ComboBox <https://www.autohotkey.com/docs/commands/GuiControls.htm#ComboBox>`_
     -
   + - `ListBox <https://www.autohotkey.com/docs/commands/GuiControls.htm#ListBox>`_
     - :class:`tkinter.Listbox`
   + - `ListView <https://www.autohotkey.com/docs/commands/GuiControls.htm#ListView>`_
     -
   + - `TreeView <https://www.autohotkey.com/docs/commands/GuiControls.htm#TreeView>`_
     - :class:`tkinter.ttk.Treeview`
   + - `Link <https://www.autohotkey.com/docs/commands/GuiControls.htm#Link>`_
     -
   + - `Hotkey <https://www.autohotkey.com/docs/commands/GuiControls.htm#Hotkey>`_
     -
   + - `DateTime <https://www.autohotkey.com/docs/commands/GuiControls.htm#DateTime>`_
     -
   + - `MonthCal <https://www.autohotkey.com/docs/commands/GuiControls.htm#MonthCal>`_
     -
   + - `Slider <https://www.autohotkey.com/docs/commands/GuiControls.htm#Slider>`_
     - :class:`tkinter.ttk.Scale`
   + - `Progress <https://www.autohotkey.com/docs/commands/GuiControls.htm#Progress>`_
     - :class:`tkinter.ttk.Progressbar`
   + - `GroupBox <https://www.autohotkey.com/docs/commands/GuiControls.htm#GroupBox>`_
     - :class:`tkinter.ttk.Labelframe`
   + - `Tab3 <https://www.autohotkey.com/docs/commands/GuiControls.htm#Tab3>`_
     - :class:`tkinter.ttk.Notebook`
   + - `StatusBar <https://www.autohotkey.com/docs/commands/GuiControls.htm#StatusBar>`_
     -
