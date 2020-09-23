def optional_ms(value):
    if value is None or value < 0:
        return -1
    else:
        return int(value * 1000)
