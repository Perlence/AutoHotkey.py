import dataclasses as dc
import functools
from typing import Callable, Union

from . import hotkey_context
from .flow import ahk_call, _wrap_callback
from .sending import _get_send_mode

__all__ = [
    "Hotstring",
    "get_hotstring_end_chars",
    "get_hotstring_mouse_reset",
    "reset_hotstring",
    "set_hotstring_end_chars",
    "set_hotstring_mouse_reset",
]


def hotstring(
    ctx,
    trigger: str,
    repl: Union[str, Callable] = None,
    *args,
    case_sensitive=False,
    conform_to_case=True,
    replace_inside_word=False,
    wait_for_end_char=True,
    omit_end_char=False,
    backspacing=True,
    priority=0,
    text=False,
    mode=None,
    key_delay=None,
    reset_recognizer=False,
):
    """hotstring(trigger: str, repl: Union[str, Callable] = None, *args, **options)

    Register a hotstring.

    By default, the hotstring is triggered when the user types the given
    *trigger* text and presses one of the end chars which initially consist of
    the following: ``-()[]{}':;"/\\,.?!\\n \\t``. If *repl* is an instance of
    :class:`str`, the user's input will be replaced with *repl*. If *repl* is a
    callable, it will be called when the hotstring is triggered.

    When the hotstring is triggered and *repl* is a callable, *repl* is called
    with the :class:`Hotstring` instance as the *hotstring* argument if the
    function supports it.

    The optional positional *args* will be passed to the *repl* when it is
    called. If you want the *repl* to be called with keyword arguments use
    :func:`functools.partial`.

    To change the end chars use the :func:`set_hotstring_end_chars` function.

    The following keyword-only arguments set the hotstring *options*:

    - **case_sensitive** – if true, the user must type the text with the exact
      case to trigger the hotstring. Defaults to ``False``.

    - **conform_to_case** – if false, the replacement is typed exactly as given
      in *repl*. Otherwise, the following rules apply:

      - If the user types the trigger text in all caps, the replacement text is
        produced in all caps.
      - If the user types the first letter in caps, the first letter of the
        replacement is also capitalized.
      - If the user types the case in any other way, the replacement is produced
        exactly as given in *repl*.

      Defaults to ``True`` for case-insensitive hotstrings. Conversely,
      case-sensitive hotstrings never conform to the case of the trigger text.

    - **replace_inside_word** – if true, the hotstring will be triggered even
      when it is inside another word; that is, when the character typed
      immediately before it is alphanumeric::

          ahkpy.hotstring("al", "airline",
                          replace_inside_word=True)

      Given the code above, typing "practical " produces "practicairline ".

      Defaults to ``False``.

    - **wait_for_end_char** – if false, an `end chars
      <#ahkpy.get_hotstring_end_chars>`_ is not required to trigger the
      hotstring. Defaults to ``True``.

    - **omit_end_char** – if true and *wait_for_end_char* is true, then the
      hotstring waits for the user to type an end char and produces the
      replacement with the end char omitted. Defaults to ``False``.

    - **backspacing** – if false, skips removing the user input that triggered
      the hotstring before producing the *repl*::

          ahkpy.hotstring("<em>", "</em>{Left 5}",
                          wait_for_end_char=False,
                          backspacing=False)

      Given the code above, typing ``<em>`` produces ``<em>|</em>``, where ``|``
      is the keyboard cursor.

      Defaults to ``True``.

    - **priority** (:class:`int`) – the priority of the `AHK thread
      <https://www.autohotkey.com/docs/misc/Threads.htm>`_ where *repl* will be
      executed if it's a callable. It must be an integer between -2147483648 and
      2147483647. Defaults to 0.

    - **text** – if true, sends the replacement text raw, without translating
      each character to a keystroke. For details, see `Text mode
      <https://www.autohotkey.com/docs/commands/Send.htm#SendText>`_. Defaults
      to ``False``.

    - **mode** – the method by which auto-replace hotstrings send their
      keystrokes. Defaults to one currently set in :attr:`Settings.send_mode`.
      For the list of valid modes refer to :func:`~ahkpy.send`.

    - **key_delay** (:class:`float`) – the delay between keystrokes produced by
      auto-backspacing and auto-replacement. Defaults to 0 for Event and Play
      modes. For more information refer to :func:`~ahkpy.send`.

    - **reset_recognizer** – if true, resets the hotstring recognizer after each
      triggering of the hotstring. To illustrate, consider the following
      hotstring::

          @ahkpy.hotstring(
              "11",
              backspacing=False,
              wait_for_end_char=False,
              replace_inside_word=True,
          )
          def eleven():
              ahkpy.send_event("xx", level=0)

      Since the above lacks the *reset_recognizer* option, typing ``111`` (three
      consecutive 1's) triggers the hotstring twice because the middle 1 is the
      *last* character of the first triggering but also the first character of
      the second triggering. By setting *reset_recognizer* to ``True``, you
      would have to type four 1's instead of three to trigger the hotstring
      twice.

      Defaults to ``False``.

    If *repl* is given, returns an instance of :class:`Hotstring`.
    Otherwise, the method works as a decorator.

    :command: `Hotstring
       <https://www.autohotkey.com/docs/commands/Hotstring.htm>`_

    .. TODO: Review this docstring.
    """
    def hotstring_decorator(repl):
        if callable(repl) and args:
            repl = functools.partial(repl, *args)
        nonlocal mode, key_delay
        mode = _get_send_mode(mode, key_delay)
        if key_delay is None and mode != "input":
            # Wanted to use Settings.key_delay for default, but zero delay
            # is a more suitable default for hotstrings.
            key_delay = 0
        hs = Hotstring(trigger, case_sensitive, replace_inside_word, context=ctx)
        hs.update(
            repl=repl,
            conform_to_case=conform_to_case,
            wait_for_end_char=wait_for_end_char,
            omit_end_char=omit_end_char,
            backspacing=backspacing,
            priority=priority,
            text=text,
            mode=mode,
            key_delay=key_delay,
            reset_recognizer=reset_recognizer,
        )
        # Enable the hotstring in case another hotstring with the same
        # 'string' existed before, but was disabled.
        hs.enable()
        return hs

    if repl is None:
        return hotstring_decorator
    return hotstring_decorator(repl)


@dc.dataclass(frozen=True)
class Hotstring:
    """Hotstring(trigger: str, case_sensitive: bool, replace_inside_word: bool, context: ahkpy.HotkeyContext)

    The immutable object that represents a registered hotstring.

    Creating an instance of :class:`!Hotstring` doesn't register it in AHK. Use
    the :meth:`HotkeyContext.hotstring` method instead.

    Hotstrings in AutoHotkey are defined by the trigger string,
    case-sensitivity, word-sensitivity (*replace_inside_word*), and the context
    in which they are created. For example, the following creates only one
    hotstring::

        hs1 = ahkpy.hotstring("btw", "by the way", case_sensitive=False)
        hs2 = ahkpy.hotstring("BTW", "by the way", case_sensitive=False)

    This is because *case_sensitive* option is set to ``False`` (the default),
    so that the hotstring will trigger regardless of the case it was typed in.

    Conversely, the following creates two separate hotstrings::

        hs1 = ahkpy.hotstring("btw", "by the way", case_sensitive=True)
        hs2 = ahkpy.hotstring("BTW", "by the way", case_sensitive=True)
    """

    trigger: str
    case_sensitive: bool
    replace_inside_word: bool
    context: 'hotkey_context.HotkeyContext'
    __slots__ = ("trigger", "case_sensitive", "replace_inside_word", "context")

    # There are no 'repl' and option fields in Hotstring object. See the
    # reasoning in the Hotkey class.

    # Case sensitivity and conformity transitions:
    #     CO <-> C1
    #     C1 <-- C --> C0

    def __post_init__(self):
        if hasattr(self.trigger, "lower") and not self.case_sensitive:
            object.__setattr__(self, "trigger", self.trigger.lower())

    def enable(self):
        """Enable the hotkey."""
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.trigger}", "", "On")

    def disable(self):
        """Disable the hotkey."""
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.trigger}", "", "Off")

    def toggle(self):
        """Enable the hotstring if it's disabled or do the opposite."""
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.trigger}", "", "Toggle")

    def _id_options(self):
        case_option = "C" if self.case_sensitive else ""
        replace_inside_option = "?" if self.replace_inside_word else "?0"
        return f"{case_option}{replace_inside_option}"

    def update(
        self, *, repl=None, conform_to_case=None, wait_for_end_char=None, omit_end_char=None, backspacing=None,
        priority=None, text=None, mode=None, key_delay=None, reset_recognizer=None,
    ):
        """Update the hotstring's *repl* and options.

        For more information about the arguments refer to
        :meth:`HotkeyContext.hotstring`.
        """
        if callable(repl):
            repl = _wrap_callback(
                repl,
                ("hotstring",),
                _bare_hotstring_handler,
                functools.partial(_hotstring_handler, hotstring=self),
            )

        options = []

        if self.case_sensitive:
            options.append("C")
        elif conform_to_case:
            options.append("C0")
        elif conform_to_case is not None:
            options.append("C1")

        if self.replace_inside_word:
            options.append("?")
        else:
            options.append("?0")

        if wait_for_end_char is False:
            options.append("*")
        elif omit_end_char:
            options.append("*0")
            options.append("O")
        else:
            if wait_for_end_char:
                options.append("*0")
            if omit_end_char is False:
                options.append("O0")

        if backspacing:
            options.append("B")
        elif backspacing is not None:
            options.append("B0")

        if key_delay is not None:
            if key_delay > 0:
                key_delay = int(key_delay * 1000)
            options.append(f"K{key_delay}")

        if priority is not None:
            options.append(f"P{priority}")

        if text:
            options.append("T")
        elif text is not None:
            options.append("T0")

        if mode == "input":
            options.append("SI")
        elif mode == "play":
            options.append("SP")
        elif mode == "event":
            options.append("SE")
        elif mode is not None:
            raise ValueError(f"{mode!r} is not a valid send mode")

        if reset_recognizer:
            options.append("Z")
        elif reset_recognizer is not None:
            options.append("Z0")

        option_str = "".join(options)

        with self.context._manager():
            ahk_call("Hotstring", f":{option_str}:{self.trigger}", repl)


def _bare_hotstring_handler(func):
    func()


def _hotstring_handler(func, hotstring):
    func(hotstring=hotstring)


def reset_hotstring():
    """Reset the hotstring recognizer.

    The script will begin waiting for an entirely new hotstring, eliminating
    from consideration anything the user has typed previously.

    :command: `Hotstring("Reset")
       <https://www.autohotkey.com/docs/commands/Hotstring.htm#Reset>`_
    """
    ahk_call("Hotstring", "Reset")


def get_hotstring_end_chars():
    """Retrieve the set of end chars.

    The default end chars are the following: ``-()[]{}':;"/\\,.?!\\n \\t``.

    :command: `Hotstring("EndChars")
       <https://www.autohotkey.com/docs/commands/Hotstring.htm#EndChars>`_
    """
    return ahk_call("Hotstring", "EndChars")


def set_hotstring_end_chars(chars: str):
    """Change the end chars.

    The end chars can only be changed globally for all hostrings at once.

    :command: `Hotstring("EndChars", NewValue)
       <https://www.autohotkey.com/docs/commands/Hotstring.htm#EndChars>`_
    """
    ahk_call("Hotstring", "EndChars", str(chars))


def get_hotstring_mouse_reset():
    """Get whether mouse clicks reset the hotstring recognizer.

    By default, any click of the left or right mouse button will reset the
    hotstring recognizer.

    :command: `Hotstring("MouseReset")
       <https://www.autohotkey.com/docs/commands/Hotstring.htm#MouseReset>`_
    """
    return ahk_call("Hotstring", "MouseReset")


def set_hotstring_mouse_reset(value: bool):
    """Set whether mouse clicks reset the hotstring recognizer.


    :command: `Hotstring("MouseReset", NewValue)
       <https://www.autohotkey.com/docs/commands/Hotstring.htm#MouseReset>`_
    """
    ahk_call("Hotstring", "MouseReset", bool(value))
