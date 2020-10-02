import inspect
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Union

from .exceptions import Error
from .flow import ahk_call, global_ahk_lock
from .settings import get_settings, optional_ms
from .unset import UNSET

__all__ = [
    "Hotkey",
    "HotkeyContext",
    "Hotstring",
    "block_input_while_sending",
    "block_input",
    "block_mouse_move",
    "get_hotstring_end_chars",
    "get_hotstring_mouse_reset",
    "get_key_name",
    "get_key_sc",
    "get_key_state",
    "get_key_vk",
    "get_physical_key_state",
    "hotkey",
    "hotstring",
    "is_key_toggled",
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
    "wait_key_pressed",
    "wait_key_released",
]


def get_key_state(key_name):
    return _get_key_state(key_name)


def get_physical_key_state(key_name):
    return _get_key_state(key_name, "P")


def is_key_toggled(key_name):
    if key_name.lower() not in {"capslock", "numlock", "scrolllock", "insert", "ins"}:
        raise ValueError("key_name must be one of CapsLock, NumLock, ScrollLock, or Insert")
    return _get_key_state(key_name, "T")


def _get_key_state(key_name, mode=None):
    result = ahk_call("GetKeyState", key_name, mode)
    if result == "":
        raise ValueError("key_name is invalid or the state of the key could not be determined")
    return bool(result)


def set_caps_lock_state(state):
    _set_key_state("SetCapsLockState", state)


def set_num_lock_state(state):
    _set_key_state("SetNumLockState", state)


def set_scroll_lock_state(state):
    _set_key_state("SetScrollLockState", state)


def _set_key_state(cmd, state):
    if isinstance(state, str) and state.lower() in {"always_on", "alwayson"}:
        state = "AlwaysOn"
    elif isinstance(state, str) and state.lower() in {"always_off", "alwaysoff"}:
        state = "AlwaysOff"
    elif state:
        state = "On"
    else:
        state = "Off"
    ahk_call(cmd, state)


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


@dataclass(frozen=True)
class BaseHotkeyContext:
    # XXX: Consider adding context options: MaxThreadsBuffer,
    # MaxThreadsPerHotkey, and InputLevel.

    def hotkey(
        self,
        key_name: str,
        func: Callable = None,
        *,
        buffer=False,
        priority=0,
        max_threads=1,
        input_level=0,
    ):
        # XXX: Consider adding arguments for '*', '~', and '$' prefix hotkey
        # modifiers.
        if key_name == "":
            raise Error("invalid key name")

        def hotkey_decorator(func):
            if not callable(func):
                raise TypeError(f"object {func!r} must be callable")

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
            # XXX: Consider implementing decorator chaining, e.g.:
            #
            #     @ahk.hotkey("F11")
            #     @ahk.hotkey("F12")
            #     def func():
            #         print("F11 or F12 was pressed")
            return hotkey_decorator

        # TODO: Handle case when func == "AltTab" or other substitutes.

        return hotkey_decorator(func)

    def remap_key(self, origin_key, destination_key, *, mode=None, level=None):
        # TODO: Handle LCtrl as the origin key.
        # TODO: Handle remapping keyboard key to a mouse button.
        @self.hotkey(f"*{origin_key}")
        def wildcard_origin():
            send("{Blind}{%s DownR}" % destination_key, mode=mode, level=level)

        @self.hotkey(f"*{origin_key} Up")
        def wildcard_origin_up():
            send("{Blind}{%s Up}" % destination_key, mode=mode, level=level)

        return RemappedKey(wildcard_origin, wildcard_origin_up)

    def hotstring(
        self,
        string: str,
        replacement: Union[str, Callable] = None,
        *,
        case_sensitive=False,
        conform_to_case=True,
        replace_inside_word=False,
        wait_for_end_char=True,
        omit_end_char=False,
        backspacing=True,
        priority=0,
        text=False,
        mode=None,
        key_delay=-1,
        reset_recognizer=False,
    ):
        def hotstring_decorator(replacement):
            hs = Hotstring(string, case_sensitive, replace_inside_word, context=self)
            hs.update(
                replacement=replacement,
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

        if replacement is None:
            return hotstring_decorator
        return hotstring_decorator(replacement)

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


@dataclass(frozen=True)
class HotkeyContext(BaseHotkeyContext):
    predicate: Callable
    __slots__ = ("predicate",)

    def __init__(self, predicate):
        signature = inspect.signature(predicate)
        if len(signature.parameters) == 0:
            def wrapper(*args):
                return bool(predicate())
        else:
            def wrapper(*args):
                return bool(predicate(*args))

        object.__setattr__(self, "predicate", wrapper)

    def _enter(self):
        ahk_call("HotkeyContext", self.predicate)

    def _exit(self):
        ahk_call("HotkeyExitContext")


@dataclass(frozen=True)
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
    #    stored in the Python Hotkey object becomes absolete and misleading.

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

        context_hash = hash(self.context)
        with self.context._manager():
            ahk_call("Hotkey", context_hash, self.key_name, func or "", option_str)


@dataclass(frozen=True)
class Hotstring:
    string: str
    case_sensitive: bool
    replace_inside_word: bool
    context: BaseHotkeyContext
    __slots__ = ("string", "case_sensitive", "replace_inside_word", "context")

    # There are no 'replacement' and option fields in Hotstring object. See the
    # reasoning in the Hotkey class.

    # Case sensitivity and conformity transitions:
    #     CO <-> C1
    #     C1 <-- C --> C0

    def __post_init__(self):
        if hasattr(self.string, "lower") and not self.case_sensitive:
            object.__setattr__(self, "string", self.string.lower())

    def disable(self):
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.string}", "", "Off")

    def enable(self):
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.string}", "", "On")

    def toggle(self):
        with self.context._manager():
            ahk_call("Hotstring", f":{self._id_options()}:{self.string}", "", "Toggle")

    def _id_options(self):
        case_option = "C" if self.case_sensitive else ""
        replace_inside_option = "?" if self.replace_inside_word else "?0"
        return f"{case_option}{replace_inside_option}"

    def update(
        self, *, replacement=None, conform_to_case=None, wait_for_end_char=None, omit_end_char=None, backspacing=None,
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
            # TODO: Handle changing replacement func.
            ahk_call("Hotstring", f":{option_str}:{self.string}", replacement or "")


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


def wait_key_pressed(key_name, logical_state=False, timeout=None) -> bool:
    return _key_wait(key_name, down=True, logical_state=logical_state, timeout=timeout)


def wait_key_released(key_name, logical_state=False, timeout=None) -> bool:
    return _key_wait(key_name, down=False, logical_state=logical_state, timeout=timeout)


def _key_wait(key_name, down=False, logical_state=False, timeout=None) -> bool:
    options = []
    if down:
        options.append("D")
    if logical_state:
        options.append("L")
    if timeout is not None:
        options.append(f"T{timeout}")
    timed_out = ahk_call("KeyWait", str(key_name), "".join(options))
    return not timed_out


@dataclass(frozen=True)
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
    # TODO: Sending "{U+0009}" and "\u0009" gives different results depending on
    # how tabs are handled in the application.
    if mode is None:
        mode = get_settings().send_mode
        if mode == "input" and (
            key_delay not in {None, UNSET} or
            key_duration not in {None, UNSET} or
            mouse_delay not in {None, UNSET}
        ):
            mode = "event"
    if mode == "input":
        send_func = send_input
    elif mode == "play":
        send_func = send_play
    elif mode == "event":
        send_func = send_event
    else:
        raise ValueError(f"{mode!r} is not a valid send mode")
    send_func(keys, level=level, key_delay=key_delay, key_duration=key_duration, mouse_delay=mouse_delay)


def send_input(keys, *, level=None, key_delay=None, key_duration=None, mouse_delay=None):
    with global_ahk_lock:
        _send_level(level)
        ahk_call("SendInput", keys)


def send_event(keys, *, level=None, key_delay=None, key_duration=None, mouse_delay=None):
    with global_ahk_lock:
        _send_level(level)
        _set_delay(key_delay, key_duration, mouse_delay)
        ahk_call("SendEvent", keys)


def send_play(keys, *, level=None, key_delay=None, key_duration=None, mouse_delay=None):
    with global_ahk_lock:
        _send_level(level)
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
    """Block user input while a Send command is in progress.

    This also blocks user input during mouse automation because mouse clicks and
    movements are implemented via the Send command.
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
