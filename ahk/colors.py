def to_hex(r, g, b):
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise TypeError("color values must be integers")
    return f"{r:x}{g:x}{b:x}"


def to_tuple(string):
    if not len(string) == 6:
        raise ValueError(f"color string '{string!r}' must be of length 6")
    r = string[:2]
    g = string[2:4]
    b = string[4:6]
    return int(r, 16), int(g, 16), int(b, 16)
