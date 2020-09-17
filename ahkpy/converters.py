def default(a, b):
    if a is not None:
        return a
    return b


def optional_ms(value):
    if value is None or value < 0:
        return -1
    else:
        return int(value * 1000)
