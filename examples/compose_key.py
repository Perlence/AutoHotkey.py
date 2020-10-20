from functools import partial

import ahkpy as ahk


def compose_send(keys, shift_keys=None):
    shift_pressed = ahk.is_key_pressed_physical("Shift")
    ahk.wait_key_released(COMPOSE)
    if shift_keys and shift_pressed:
        ahk.send(shift_keys)
    else:
        ahk.send(keys)


COMPOSE = "CapsLock"

ahk.hotkey(f"{COMPOSE} & -", partial(compose_send, "–", "—"))  # dashes
ahk.hotkey(f"{COMPOSE} & Tab", partial(compose_send, "{U+0009}"))  # tab
ahk.hotkey(f"{COMPOSE} & '", partial(compose_send, "\u0301", "\u0308"))  # á ä
ahk.hotkey(f"{COMPOSE} & 6", partial(compose_send, "\u0302"))  # â
ahk.hotkey(f"{COMPOSE} & `", partial(compose_send, "\u0300", "\u0303"))  # à ã
ahk.hotkey(f"{COMPOSE} & o", partial(compose_send, "\u030A"))  # å
ahk.hotkey(f"{COMPOSE} & 2", partial(compose_send, "²"))
