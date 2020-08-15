def identity(a):
    return a


def default(a, b, func=identity, *, none=None):
    if func is not identity:
        func, a, b = a, b, func
    if a is not none:
        return func(a)
    return b


def optional_ms(value):
    if value is None or value < 0:
        return -1
    else:
        return int(value * 1000)
