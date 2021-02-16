Advanced Usage
==============

This document covers some of AutoHotkey.py's more advanced features.


.. index::
   single: global autohotkey lock

Threading
---------

In Python, the :mod:`threading` module can improve the responsiveness of
applications that accept user input while other tasks are running in the
background. A related use case is running I/O in parallel with computations in
another thread. These are actual OS threads, as opposed to AHK `pseudo-threads
<https://www.autohotkey.com/docs/misc/Threads.htm>`_.

AutoHotkey.py calls AHK functions from Python by registering a callback in AHK
with `RegisterCallback
<https://www.autohotkey.com/docs/commands/RegisterCallback.htm>`_. *These
callbacks are not thread-safe.* That is, while the *main thread* is busy
executing an AHK function, calling another AHK function from *another thread*
yields unpredictable results. It may even crash the program.

Thus, the *global AutoHotkey lock* (GAL) was introduced. GAL ensures that only
one OS thread interacts with AHK at a time.

For background threads to work, the main thread must also be crunching Python
code, for example, actively waiting for the background threads to finish.
However, calling :meth:`threading.Thread.join` in the main thread blocks AHK
message queue handling. In such cases, AHK cannot handle hotkeys and other
callbacks.

Instead, let AHK handle its message queue by calling :func:`ahkpy.sleep`
repeatedly while checking that the background thread is alive::

   import threading
   th = threading.Thread(target=some_worker)
   th.start()
   while th.is_alive():
       ahkpy.sleep(0.01)


asyncio
-------

AutoHotkey.py works well with :mod:`asyncio`. When starting a long-running loop,
schedule the :func:`ahkpy.sleep` call repeatedly. This gives AHK time to process
its message queue::

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
