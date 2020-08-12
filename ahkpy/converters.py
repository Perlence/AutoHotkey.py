def identity(a):
    return a


def default(a, b, func=identity):
    if func is not identity:
        func, a, b = a, b, func
    if a is not None:
        return func(a)
    return b


def optional_ms(value):
    if value is None:
        return -1
    else:
        return int(value * 1000)
