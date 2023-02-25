import dataclasses as dc
import functools
from typing import Callable

from . import hotkey_context
from .flow import ahk_call, _wrap_callback

__all__ = [
    "Hotkey",
]


def hotkey(
    ctx,
    key_name: str,
    func: Callable = None,
    *args,
    buffer=False,
    priority=0,
    max_threads=1,
    input_level=0,
):
    """hotkey(key_name: str, func: Callable = None, *args, **options)

    Register *func* to be called when *key_name* is pressed.

    For valid *key_name* values refer to `Hotkey Modifier Symbols
    <https://www.autohotkey.com/docs/Hotkeys.htm#Symbols>`_ and `List of Keys
    <https://www.autohotkey.com/docs/KeyList.htm>`_.

    When the hotkey is triggered, *func* is called with the :class:`Hotkey`
    instance as the *hotkey* argument if the function supports it::

        ahkpy.hotkey("F1", lambda hotkey: print(hotkey))

    Pressing :kbd:`F1` prints the following::

        Hotkey(key_name='F1', context=HotkeyContext(active_when=None))

    The optional positional *args* will be passed to the *func* when it is
    called. If you want the *func* to be called with keyword arguments use
    :func:`functools.partial`.

    The following keyword-only arguments set the hotkey *options*:

    :param bool buffer: causes the hotkey to buffer rather than ignore
        keypresses when the *max_threads* limit has been reached. Defaults to
        ``False``.

    :param int priority: the priority of the `AHK thread
        <https://www.autohotkey.com/docs/misc/Threads.htm>`__ where *func* will
        be executed. It must be an integer between -2147483648 and 2147483647.
        Defaults to 0.

    :param int max_threads: the number of keypresses AHK can handle
        concurrently. Defaults to 1.

    :param int input_level: the `input level
        <https://www.autohotkey.com/docs/commands/_InputLevel.htm>`_ of the
        hotkey. Defaults to 0.

    If *func* is given, returns an instance of :class:`Hotkey`. Otherwise, the
    method works as a decorator::

        @ahkpy.hotkey("F1")
        def hello():
            ahk.message_box("Hello!")

        assert isinstance(hello, ahkpy.Hotkey)

    :command: `Hotkey <https://www.autohotkey.com/docs/commands/Hotkey.htm>`_
    """
    # TODO: Consider adding arguments for '*', '~', and '$' prefix hotkey
    # modifiers.
    if not key_name:
        raise ValueError("key_name must not be blank")

    def hotkey_decorator(func):
        if args:
            func = functools.partial(func, *args)
        hk = Hotkey(key_name, context=ctx)
        hk.update(
            func=func,
            buffer=buffer,
            priority=priority,
            max_threads=max_threads,
            input_level=input_level,
        )
        hk.enable()
        return hk

    if func is None:
        # TODO: Consider implementing decorator chaining, e.g.:
        #
        #     @ahk.hotkey("F11")
        #     @ahk.hotkey("F12")
        #     def func():
        #         print("F11 or F12 was pressed")
        return hotkey_decorator

    # TODO: Handle case when func == "AltTab" or other substitutes.

    return hotkey_decorator(func)


@dc.dataclass(frozen=True)
class Hotkey:
    """Hotkey(key_name: str, context: ahkpy.HotkeyContext)

    The immutable object representing a hotkey registered in the given context.

    Creating an instance of :class:`!Hotkey` doesn't register it in AHK. Use the
    :meth:`HotkeyContext.hotkey` method instead.
    """

    key_name: str
    context: 'hotkey_context.HotkeyContext'
    __slots__ = ("key_name", "context")

    # I decided not to have 'func' and hotkey options as fields, because:
    #
    # 1. There's no way to get the option's value from an existing Hotkey. This
    #    means that the option must be stored in the Python Hotkey object.
    # 2. There's always a chance of setting an option in AHK but failing to
    #    store it in Python. Likewise, an option may be stored in Python, but
    #    not set in AHK yet.
    # 3. An option may be changed from the AHK side. In this case the value
    #    stored in the Python Hotkey object becomes obsolete and misleading.

    def enable(self):
        """Enable the hotkey."""
        with self.context._manager():
            ahk_call("HotkeySpecial", self.key_name, "On")

    def disable(self):
        """Disable the hotkey."""
        with self.context._manager():
            ahk_call("HotkeySpecial", self.key_name, "Off")

    def toggle(self):
        """Enable the hotkey if it's disabled or do the opposite."""
        with self.context._manager():
            ahk_call("HotkeySpecial", self.key_name, "Toggle")

    def update(self, *, func=None, buffer=None, priority=None, max_threads=None, input_level=None):
        """Update the hotkey callback and options.

        For more information about the arguments refer to
        :meth:`HotkeyContext.hotkey`.
        """
        if func is not None:
            if not callable(func):
                raise TypeError(f"object {func!r} must be callable")

            func = _wrap_callback(
                func,
                ("hotkey",),
                _bare_hotkey_handler,
                functools.partial(_hotkey_handler, hotkey=self),
            )

        options = []

        if buffer:
            options.append("B")
        elif buffer is not None:
            options.append("B0")

        if priority is not None:
            options.append(f"P{priority}")

        if max_threads is not None:
            options.append(f"T{max_threads}")

        if input_level is not None:
            options.append(f"I{input_level}")

        option_str = "".join(options)

        with self.context._manager():
            ahk_call("Hotkey", self.key_name, func, option_str)


def _bare_hotkey_handler(func):
    func()


def _hotkey_handler(func, hotkey):
    func(hotkey=hotkey)
