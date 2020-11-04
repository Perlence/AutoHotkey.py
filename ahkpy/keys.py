import dataclasses as dc
import functools
import inspect
from contextlib import contextmanager
from typing import Callable, Union

from .exceptions import Error
from .flow import ahk_call, global_ahk_lock
from .settings import get_settings, optional_ms
from .unset import UNSET

__all__ = [
    "Hotkey",
    "HotkeyContext",
    "Hotstring",
    "RemappedKey",
    "block_input_while_sending",
    "block_input",
    "block_mouse_move",
    "default_context",
    "get_caps_lock_state",
    "get_hotstring_end_chars",
    "get_hotstring_mouse_reset",
    "get_insert_state",
    "get_key_name",
    "get_key_sc",
    "get_key_vk",
    "get_num_lock_state",
    "get_scroll_lock_state",
    "hotkey",
    "hotstring",
    "is_key_pressed_logical",
    "is_key_pressed",
    "remap_key",
    "reset_hotstring",
    "send_event",
    "send_input",
    "send_play",
    "send",
    "set_caps_lock_state",
    "set_hotstring_end_chars",
    "set_hotstring_mouse_reset",
    "set_num_lock_state",
    "set_scroll_lock_state",
    "wait_key_pressed_logical",
    "wait_key_pressed",
    "wait_key_released_logical",
    "wait_key_released",
]


def is_key_pressed(key_name):
    return _get_key_state(key_name, "P")


def is_key_pressed_logical(key_name):
    return _get_key_state(key_name)


def get_caps_lock_state():
    return _get_key_state("CapsLock", "T")


def get_num_lock_state():
    return _get_key_state("NumLock", "T")


def get_scroll_lock_state():
    return _get_key_state("ScrollLock", "T")


def get_insert_state():
    return _get_key_state("Insert", "T")


def _get_key_state(key_name, mode=None):
    result = ahk_call("GetKeyState", key_name, mode)
    if result == "":
        raise ValueError(f"{key_name!r} is not a valid key or the state of the key could not be determined")
    return bool(result)


def set_caps_lock_state(state: bool, always=False):
    _set_key_state("SetCapsLockState", state, always)


def set_num_lock_state(state: bool, always=False):
    _set_key_state("SetNumLockState", state, always)


def set_scroll_lock_state(state: bool, always=False):
    _set_key_state("SetScrollLockState", state, always)


def _set_key_state(cmd, state, always):
    if state:
        state = "On"
    else:
        state = "Off"
    if always:
        state = f"Always{state}"
    ahk_call(cmd, state)


def wait_key_pressed(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=True, logical=False, timeout=timeout)


def wait_key_released(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=False, logical=False, timeout=timeout)


def wait_key_pressed_logical(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=True, logical=True, timeout=timeout)


def wait_key_released_logical(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=False, logical=True, timeout=timeout)


def _key_wait(key_name, down=False, logical=False, timeout=None) -> bool:
    options = []
    if down:
        options.append("D")
    if logical:
        options.append("L")
    if timeout is not None:
        options.append(f"T{timeout}")
    timed_out = ahk_call("KeyWait", str(key_name), "".join(options))
    return not timed_out


def get_key_name(key):
    """Return the name of a key."""
    return str(_get_key("GetKeyName", key))


def get_key_vk(key):
    """Return the virtual key code of a key."""
    return _get_key("GetKeyVK", key)


def get_key_sc(key):
    """Return the scan code of a key."""
    return _get_key("GetKeySC", key)


def _get_key(cmd, key):
    result = ahk_call(cmd, str(key))
    if not result:
        raise ValueError(f"{key!r} is not a valid key")
    return result


@dc.dataclass(frozen=True)
class BaseHotkeyContext:
    # TODO: Consider adding context options: MaxThreadsBuffer,
    # MaxThreadsPerHotkey, and InputLevel.

    def hotkey(
        self,
        key_name: str,
        func: Callable = None,
        *args,
        buffer=False,
        priority=0,
        max_threads=1,
        input_level=0,
    ):
        """Register *func* to be called when *key_name* is pressed.

        For valid *key_name* values refer to `Hotkey Modifier Symbols
        <https://www.autohotkey.com/docs/Hotkeys.htm#Symbols>`_ and `List of
        Keys <https://www.autohotkey.com/docs/KeyList.htm>`_.

        The optional positional *args* will be passed to the *func* when it is
        called. If you want the *func* to be called with keyword arguments use
        :func:`functools.partial`.

        The following keyword-only arguments set the hotkey options:

        :param buffer: causes the hotkey to buffer rather than ignore keypresses
           when the *max_threads* limit has been reached. Defaults to ``False``.

        :param priority: the priority of the AHK thread where *func* will be
           executed. It must be an :class:`int` between -2147483648 and
           2147483647. Defaults to 0.

        :param max_threads: the number of keypresses AHK can handle
           concurrently. Defaults to 1.

        :param input_level: the `input level
           <https://www.autohotkey.com/docs/commands/_InputLevel.htm>`_ of the
           hotkey. Defaults to 0.

        If *func* is omitted, the method works as a decorator::

            @ahkpy.hotkey("F1")
            def hello():
                ahk.message_box("Hello!")

            assert isinstance(hello, ahkpy.Hotkey)

        AutoHotkey command: `Hotkey
        <https://www.autohotkey.com/docs/commands/Hotkey.htm>`_.
        """
        # TODO: Consider adding arguments for '*', '~', and '$' prefix hotkey
        # modifiers.
        if key_name == "":
            raise Error("invalid key name")

        def hotkey_decorator(func):
            if args:
                func = functools.partial(func, *args)
            hk = Hotkey(key_name, context=self)
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

    def remap_key(self, origin_key, destination_key, *, mode=None, level=None):
        """Remap *origin_key* to *destination_key*.

        For valid keys refer to `List of Keys
        <https://www.autohotkey.com/docs/KeyList.htm>`_.

        The optional keyword-only *mode* and *level* arguments are passed to the
        :func:`~ahkpy.send` function that will send the *destination_key* when
        the user presses the *origin_key*.

        For more information refer to `Remapping Keys
        <https://www.autohotkey.com/docs/misc/Remap.htm>`_.
        """
        mouse = destination_key.lower() in {"lbutton", "rbutton", "mbutton", "xbutton1", "xbutton2"}
        if mouse:
            def wildcard_origin():
                if not is_key_pressed(destination_key):
                    send("{Blind}{%s DownR}" % destination_key, mode=mode, level=level, mouse_delay=-1)

            def wildcard_origin_up():
                send("{Blind}{%s Up}" % destination_key, mode=mode, level=level, mouse_delay=-1)
        else:
            ctrl_to_alt = (
                origin_key.lower() in {"ctrl", "lctrl", "rctrl"} and
                destination_key.lower() in {"alt", "lalt", "ralt"}
            )
            if ctrl_to_alt:
                def wildcard_origin():
                    send(
                        "{Blind}{%s Up}{%s DownR}" % (origin_key, destination_key),
                        mode=mode,
                        level=level,
                        key_delay=-1,
                    )
            else:
                def wildcard_origin():
                    send("{Blind}{%s DownR}" % destination_key, mode=mode, level=level, key_delay=-1)

            def wildcard_origin_up():
                send("{Blind}{%s Up}" % destination_key, mode=mode, level=level, key_delay=-1)

        wildcard_origin = self.hotkey(f"*{origin_key}", wildcard_origin)
        wildcard_origin_up = self.hotkey(f"*{origin_key} Up", wildcard_origin_up)
        return RemappedKey(wildcard_origin, wildcard_origin_up)

    def hotstring(
        self,
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
        """Register a hotstring.

        By default, the hotstring is triggered when the user types the given
        *trigger* text and presses one of the `end chars
        <https://www.autohotkey.com/docs/Hotstrings.htm#EndChars>`_. If *repl*
        is an instance of :class:`str`, the user's input will be replaced with
        *repl*. If *repl* is a callable, it will be called when the hotstring is
        triggered.

        .. TODO: Document end chars.

        The optional positional *args* will be passed to the *repl* when it is
        called. If you want the *repl* to be called with keyword arguments use
        :func:`functools.partial`.

        The following keyword-only arguments set the hotstring options:

        :param case_sensitive: if ``True``, the user must type the text with the
           exact case to trigger the hotstring. Defaults to ``False``.

        :param conform_to_case: if ``False``, the replacement is typed exactly
           as given in *repl*. Otherwise, the following rules apply:

           - If the user types the trigger text in all caps, the replacement
             text is produced in all caps.
           - If the user types the first letter in caps, the first letter of the
             replacement is also capitalized.
           - If the user types the case in any other way, the replacement is
             produced exactly as given in *repl*.

           Defaults to ``True`` for case-insensitive hotstrings. Conversely,
           case-sensitive hotstrings never conform to the case of the trigger
           text.

        :param replace_inside_word: if ``True``, the hotstring will be triggered
           even when it is inside another word; that is, when the character
           typed immediately before it is alphanumeric::

               ahkpy.hotstring("al", "airline",
                               replace_inside_word=True)

           Given the code above, typing "practical " produces "practicairline ".

           Defaults to ``False``.

        :param wait_for_end_char: if ``False``, an `end char
           <https://www.autohotkey.com/docs/Hotstrings.htm#EndChars>`_ is not
           required to trigger the hotstring. Defaults to ``True``.

        :param omit_end_char: if ``True`` and *wait_for_end_char* is ``True``,
           then the hotstring waits for the user to type an end char and
           produces the replacement with the end char omitted. Defaults to
           ``False``.

        :param backspacing: if ``False``, skips removing the user input that
           triggered the hotstring before producing the *repl*::

               ahkpy.hotstring("<em>", "</em>{Left 5}",
                               wait_for_end_char=false,
                               backspacing=False)

           Given the code above, typing ``<em>`` produces ``<em>|</em>``, where
           ``|`` is the keyboard cursor.

           Defaults to ``True``.

        :param priority: the priority of the AHK thread where *repl* will be
           executed if it's a callable. It must be an :class:`int` between
           -2147483648 and 2147483647. Defaults to 0.

        :param text: if ``True``, sends the replacement text raw, without
           translating each character to a keystroke. For details, see `Text
           mode <https://www.autohotkey.com/docs/commands/Send.htm#SendText>`_.
           Defaults to ``False``.

           .. TODO: Check `r and `n characters in Text mode.

        :param mode: the method by which auto-replace hotstrings send their
           keystrokes. Defaults to one currently set in
           :attr:`Settings.send_mode`. For the list of valid modes refer to
           :func:`ahkpy.send`.

        :param key_delay: the delay between keystrokes produced by
           auto-backspacing and auto-replacement. Defaults to 0 for Event and
           Play modes. For more information refer to :func:`ahkpy.send`.

        :param reset_recognizer: if ``True``, resets the hotstring recognizer
           after each triggering of the hotstring. To illustrate, consider the
           following hotstring::

               @ahkpy.hotstring(
                   "11",
                   backspacing=False,
                   wait_for_end_char=False,
                   replace_inside_word=True,
               )
               def eleven():
                   ahkpy.send_event("xx", level=0)

           Since the above lacks the *reset_recognizer* option, typing ``111``
           (three consecutive 1's) triggers the hotstring twice because the
           middle 1 is the *last* character of the first triggering but also the
           first character of the second triggering. By setting
           *reset_recognizer* to ``True``, you would have to type four 1's
           instead of three to trigger the hotstring twice.

           Defaults to ``False``.

        AutoHotkey function: `Hotstring
        <https://www.autohotkey.com/docs/commands/Hotstring.htm>`_.
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
            hs = Hotstring(trigger, case_sensitive, replace_inside_word, context=self)
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

    @contextmanager
    def _manager(self):
        # I don't want to make BaseHotkeyContext a Python context manager,
        # because the end users will be tempted to use it as such, e.g:
        #
        #     with hotkey_context(lambda: ...):
        #         hotkey(...)
        #
        # This approach has a number of issues that can be mitigated, but better
        # be avoided:
        #
        # 1. Current context must be stored in a thread-local storage in order
        #    to be referenced by hotkey(). This can be solved by returning the
        #    context as `with ... as ctx`.
        # 2. Nested contexts become possible, but implementing them is not
        #    trivial.
        #
        # Instead, the following is the chosen way to use the hotkey contexts:
        #
        #     ctx = hotkey_context(lambda: ...)
        #     ctx.hotkey(...)

        with global_ahk_lock:
            self._enter()
            try:
                yield
            finally:
                self._exit()

    def _enter(self):
        pass

    def _exit(self):
        pass


default_context = BaseHotkeyContext()
hotkey = default_context.hotkey
remap_key = default_context.remap_key
hotstring = default_context.hotstring


@dc.dataclass(frozen=True)
class HotkeyContext(BaseHotkeyContext):
    """The context-specific hotkey factory. It's used to create hotkeys and key
    remappings that will be active only when the given *predicate* evaluates to
    ``True``.

    The *predicate* argument is a callable that is executed every time the user
    presses the hotkey or – in case of a key remapping – the origin key. The
    predicate takes either zero or one positional argument. In case of latter,
    the predicate will be called with the *key_name* of the
    :meth:`~ahkpy.keys.BaseHotkeyContext.hotkey` that was pressed by the user.

    In the following example pressing the :kbd:`F1` key shows the message only
    when the mouse cursor is over the taskbar::

        def is_mouse_over_taskbar():
            return ahkpy.get_window_under_mouse().class_name == "Shell_TrayWnd"

        ctx = ahkpy.HotkeyContext(is_mouse_over_taskbar)
        ctx.hotkey("F1", ahkpy.message_box, "Pressed F1 over the taskbar.")

    AutoHotkey command: `Hotkey, If, % FunctionObject
    <https://www.autohotkey.com/docs/commands/Hotkey.htm#IfFn>`_.
    """

    predicate: Callable
    __slots__ = ("predicate",)

    def __init__(self, predicate):
        signature = inspect.signature(predicate)
        if len(signature.parameters) == 0:
            def wrapped_predicate(hotkey):
                return bool(predicate())
        else:
            def wrapped_predicate(hotkey):
                return bool(predicate(hotkey))

        wrapped_predicate = functools.wraps(predicate)(wrapped_predicate)
        object.__setattr__(self, "predicate", wrapped_predicate)

    def _enter(self):
        ahk_call("HotkeyContext", self.predicate)

    def _exit(self):
        ahk_call("HotkeyExitContext")


@dc.dataclass(frozen=True)
class Hotkey:
    key_name: str
    context: BaseHotkeyContext
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
        with self.context._manager():
            ahk_call("HotkeySpecial", self.key_name, "On")

    def disable(self):
        with self.context._manager():
            ahk_call("HotkeySpecial", self.key_name, "Off")

    def toggle(self):
        with self.context._manager():
            ahk_call("HotkeySpecial", self.key_name, "Toggle")

    def update(self, *, func=None, buffer=None, priority=None, max_threads=None, input_level=None):
        if not callable(func):
            raise TypeError(f"object {func!r} must be callable")

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
            ahk_call("Hotkey", self.key_name, func or "", option_str)


@dc.dataclass(frozen=True)
class Hotstring:
    trigger: str
    case_sensitive: bool
    replace_inside_word: bool
    context: BaseHotkeyContext
    __slots__ = ("trigger", "case_sensitive", "replace_inside_word", "context")

    # There are no 'repl' and option fields in Hotstring object. See the
    # reasoning in the Hotkey class.

    # Case sensitivity and conformity transitions:
    #     CO <-> C1
    #     C1 <-- C --> C0

    def __post_init__(self):
        if hasattr(self.trigger, "lower") and not self.case_sensitive:
            object.__setattr__(self, "trigger", self.trigger.lower())

    def disable(self):
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.trigger}", "", "Off")

    def enable(self):
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.trigger}", "", "On")

    def toggle(self):
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

        # TODO: The hotstring is not replaced when the mode is set to Input
        # explicitly.
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
            ahk_call("Hotstring", f":{option_str}:{self.trigger}", repl or "")


def reset_hotstring():
    ahk_call("Hotstring", "Reset")


def get_hotstring_end_chars():
    return ahk_call("Hotstring", "EndChars")


def set_hotstring_end_chars(chars):
    ahk_call("Hotstring", "EndChars", str(chars))


def get_hotstring_mouse_reset():
    return ahk_call("Hotstring", "MouseReset")


def set_hotstring_mouse_reset(value):
    ahk_call("Hotstring", "MouseReset", bool(value))


@dc.dataclass(frozen=True)
class RemappedKey:
    wildcard_origin: Hotkey
    wildcard_origin_up: Hotkey
    __slots__ = ("wildcard_origin", "wildcard_origin_up")

    def enable(self):
        self.wildcard_origin.enable()
        self.wildcard_origin_up.enable()

    def disable(self):
        self.wildcard_origin.disable()
        self.wildcard_origin_up.disable()

    def toggle(self):
        self.wildcard_origin.toggle()
        self.wildcard_origin_up.toggle()


def send(keys, *, mode=None, level=None, key_delay=None, key_duration=None, mouse_delay=None):
    """Send simulated keystrokes and mouse clicks to the active window."""
    # TODO: Sending "{U+0009}" and "\u0009" gives different results depending on
    # how tabs are handled in the application.
    # TODO: Consider adding *blind*, *text*, and *raw* arguments.
    mode = _get_send_mode(mode, key_delay, key_duration, mouse_delay)
    if mode == "input":
        send_func = send_input
    elif mode == "play":
        send_func = send_play
    elif mode == "event":
        send_func = send_event
    else:
        raise ValueError(f"{mode!r} is not a valid send mode")
    send_func(keys, level=level, key_delay=key_delay, key_duration=key_duration, mouse_delay=mouse_delay)


def _get_send_mode(mode=None, key_delay=None, key_duration=None, mouse_delay=None):
    if mode is not None:
        return mode
    mode = get_settings().send_mode
    if mode == "input" and (
        isinstance(key_delay, (int, float)) and key_delay >= 0 or
        isinstance(key_duration, (int, float)) and key_duration >= 0 or
        isinstance(mouse_delay, (int, float)) and mouse_delay >= 0
    ):
        return "event"
    return mode


def send_input(keys, *, level=None, **rest):
    with global_ahk_lock:
        _send_level(level)
        ahk_call("SendInput", keys)


def send_event(keys, *, level=None, key_delay=None, key_duration=None, mouse_delay=None):
    with global_ahk_lock:
        _send_level(level)
        _set_delay(key_delay, key_duration, mouse_delay)
        ahk_call("SendEvent", keys)


def send_play(keys, *, key_delay=None, key_duration=None, mouse_delay=None, **rest):
    with global_ahk_lock:
        # SendPlay is not affected by SendLevel.
        _set_delay(key_delay, key_duration, mouse_delay, play=True)
        ahk_call("SendPlay", keys)


def _send_level(level):
    if level is None:
        level = get_settings().send_level
    elif not 0 <= level <= 100:
        raise ValueError("level must be between 0 and 100")
    ahk_call("SendLevel", int(level))


def _set_delay(key_delay=None, key_duration=None, mouse_delay=None, play=False):
    settings = get_settings()
    if play:
        if key_delay is not UNSET and key_duration is not UNSET:
            ahk_call(
                "SetKeyDelay",
                optional_ms(key_delay if key_delay is not None else settings.key_delay_play),
                optional_ms(key_duration if key_duration is not None else settings.key_duration_play),
                "Play",
            )
        if mouse_delay is not UNSET:
            ahk_call(
                "SetMouseDelay",
                optional_ms(mouse_delay if mouse_delay is not None else settings.mouse_delay_play),
                "Play",
            )
    else:
        if key_delay is not UNSET and key_duration is not UNSET:
            ahk_call(
                "SetKeyDelay",
                optional_ms(key_delay if key_delay is not None else settings.key_delay),
                optional_ms(key_duration if key_duration is not None else settings.key_duration),
            )
        if mouse_delay is not UNSET:
            ahk_call(
                "SetMouseDelay",
                optional_ms(mouse_delay if mouse_delay is not None else settings.mouse_delay),
            )


@contextmanager
def block_input():
    """Block all user input unconditionally."""
    ahk_call("BlockInput", "On")
    yield
    ahk_call("BlockInput", "Off")


@contextmanager
def block_input_while_sending():
    """Block user input while a :func:`send` is in progress.

    This also blocks user input during mouse automation because mouse clicks and
    movements are implemented using the :func:`send` function.
    """
    ahk_call("BlockInput", "Send")
    yield
    ahk_call("BlockInput", "Default")


@contextmanager
def block_mouse_move():
    """Block the mouse cursor movement."""
    ahk_call("BlockInput", "MouseMove")
    yield
    ahk_call("BlockInput", "MouseMoveOff")
