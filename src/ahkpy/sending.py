from .flow import ahk_call, global_ahk_lock
from .settings import get_settings, optional_ms
from .unset import UNSET

__all__ = [
    "send_event",
    "send_input",
    "send_play",
    "send",
]


def send(keys: str, *, mode=None, level=None, key_delay=None, key_duration=None, mouse_delay=None):
    """send(keys: str, *, mode=None, **options)

    Send simulated keystrokes and mouse clicks to the active window.

    The *keys* argument is an encoded sequence of keys. For valid *keys* refer
    to `Send <https://www.autohotkey.com/docs/commands/Send.htm#Parameters>`__.

    :param str mode: the mode that is used to send keys and clicks. Takes one of
       the following values: ``"input"``, ``"event"``, ``"play"``. Defaults to
       one currently set in :attr:`Settings.send_mode`. If any of *key_delay*,
       *key_duration*, or *mouse_delay* arguments are given, and the current
       mode is Input, then reverts to the Event mode. For differences between
       the modes refer to `Send variants
       <https://www.autohotkey.com/docs/commands/Send.htm#Send_variants>`_.

    :param int level: controls which artificial keyboard and mouse events are
       ignored by hotkeys and hotstrings. It must be an integer between 0 and
       100. Has no effect in the Play mode. Defaults to one currently set in
       :attr:`Settings.send_level`. For more information refer to `SendLevel
       Remarks
       <https://www.autohotkey.com/docs/commands/SendLevel.htm#General_Remarks>`_.

    :param float key_delay: the delay in seconds after each keystroke. Defaults
       to one currently set in :attr:`Settings.key_delay` or
       :attr:`Settings.key_delay_play`. For more information refer to
       `SetKeyDelay Remarks
       <https://www.autohotkey.com/docs/commands/SetKeyDelay.htm#Remarks>`_.

    :param float key_duration: the delay in seconds after pressing the key and
       before releasing it. Defaults to one currently set in
       :attr:`Settings.key_duration` or :attr:`Settings.key_duration_play`. For
       more information refer to `SetKeyDelay Remarks`_.

    :param float mouse_delay: the delay after each mouse movement or click.
       Defaults to one currently set in :attr:`Settings.mouse_delay` or
       :attr:`Settings.mouse_delay_play`. For more information refer to
       `SetMouseDelay Remarks
       <https://www.autohotkey.com/docs/commands/SetMouseDelay.htm#Remarks>`_.

    :command: `Send <https://www.autohotkey.com/docs/commands/Send.htm>`_
    """
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
    """Send simulated keystrokes and mouse clicks using the Input mode."""
    with global_ahk_lock:
        _send_level(level)
        ahk_call("SendInput", keys)


def send_event(keys, *, level=None, key_delay=None, key_duration=None, mouse_delay=None):
    """Send simulated keystrokes and mouse clicks using the Event mode."""
    with global_ahk_lock:
        _send_level(level)
        _set_delay(key_delay, key_duration, mouse_delay)
        ahk_call("SendEvent", keys)


def send_play(keys, *, key_delay=None, key_duration=None, mouse_delay=None, **rest):
    """Send simulated keystrokes and mouse clicks using the Play mode."""
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
