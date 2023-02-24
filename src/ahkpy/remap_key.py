import dataclasses as dc

from .hotkey import Hotkey
from .key_state import is_key_pressed
from .sending import send

__all__ = [
    "RemappedKey",
]


def remap_key(ctx, origin_key, destination_key, *, mode=None, level=None):
    """Remap *origin_key* to *destination_key*.

    Returns an instance of :class:`RemappedKey`.

    For valid keys refer to `List of Keys
    <https://www.autohotkey.com/docs/KeyList.htm>`_.

    The optional keyword-only *mode* and *level* arguments are passed to the
    :func:`send` function that will send the *destination_key* when the user
    presses the *origin_key*.

    For more information refer to `Remapping Keys
    <https://www.autohotkey.com/docs/misc/Remap.htm>`_.
    """
    mouse = destination_key.lower() in {"lbutton", "rbutton", "mbutton", "xbutton1", "xbutton2"}
    if mouse:
        def origin_hotkey():
            if not is_key_pressed(destination_key):
                send("{Blind}{%s DownR}" % destination_key, mode=mode, level=level, mouse_delay=-1)

        def origin_up_hotkey():
            send("{Blind}{%s Up}" % destination_key, mode=mode, level=level, mouse_delay=-1)
    else:
        ctrl_to_alt = (
            origin_key.lower() in {"ctrl", "lctrl", "rctrl"} and
            destination_key.lower() in {"alt", "lalt", "ralt"}
        )
        if ctrl_to_alt:
            def origin_hotkey():
                send(
                    "{Blind}{%s Up}{%s DownR}" % (origin_key, destination_key),
                    mode=mode,
                    level=level,
                    key_delay=-1,
                )
        else:
            def origin_hotkey():
                send("{Blind}{%s DownR}" % destination_key, mode=mode, level=level, key_delay=-1)

        def origin_up_hotkey():
            send("{Blind}{%s Up}" % destination_key, mode=mode, level=level, key_delay=-1)

    origin_hotkey = ctx.hotkey(f"*{origin_key}", origin_hotkey)
    origin_up_hotkey = ctx.hotkey(f"*{origin_key} Up", origin_up_hotkey)
    return RemappedKey(origin_hotkey, origin_up_hotkey)


@dc.dataclass(frozen=True)
class RemappedKey:
    """RemappedKey(origin_hotkey: ahkpy.Hotkey, origin_up_hotkey: ahkpy.Hotkey)

    The immutable object that represents a remapped key.

    Creating an instance of :class:`!RemappedKey` doesn't register it in AHK.
    Use the :meth:`HotkeyContext.remap_key` method instead.
    """

    origin_hotkey: Hotkey
    origin_up_hotkey: Hotkey
    __slots__ = ("origin_hotkey", "origin_up_hotkey")

    def enable(self):
        """Enable the key remapping."""
        self.origin_hotkey.enable()
        self.origin_up_hotkey.enable()

    def disable(self):
        """Disable the key remapping."""
        self.origin_hotkey.disable()
        self.origin_up_hotkey.disable()

    def toggle(self):
        """Enable the key remapping if it's disabled or do the opposite."""
        self.origin_hotkey.toggle()
        self.origin_up_hotkey.toggle()
