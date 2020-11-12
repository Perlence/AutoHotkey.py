# flake8: noqa

import timeit

import _ahk

# %%

loops = 5000
t = timeit.repeat("_ahk.call('EnvGet', 'TEMP')", repeat=20, number=loops, globals={"_ahk": _ahk})
print(min(t) / loops * 1e6, max(t) / loops * 1e6)  # usec
# 5000 loops, best of 5: 52.4 usec per loop
# 41-45 usec

# %%

from ctypes import CFUNCTYPE, py_object, c_bool, c_wchar_p, c_void_p, create_unicode_buffer

ahk_call2 = CFUNCTYPE(
    # py_object,
    # c_bool,
    c_wchar_p,
    c_wchar_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p,
    # c_wchar_p, # result
)
call = ahk_call2(_ahk.call2)

# res = create_unicode_buffer(256)
# print(call('EnvGet2', 'TEMP', None, None, None, None, None, None, None, None, None, None, res))
# print(repr(res.value))

print(repr(call('EnvGet2', 'TEMP', None, None, None, None, None, None, None, None, None, None)))

# res = c_void_p()
# print(call('EnvGet2', 'TEMP', None, None, None, None, None, None, None, None, None, None, byref(res)))
# print(res)
# print("END")

t = timeit.repeat(
    """\
# res = create_unicode_buffer(256)
# assert call('EnvGet2', 'TEMP', None, None, None, None, None, None, None, None, None, None, res)
# assert res.value
assert call('EnvGet2', 'TEMP', None, None, None, None, None, None, None, None, None, None)
""",
    repeat=20,
    number=loops,
    globals={"call": call, "create_unicode_buffer": create_unicode_buffer},
)
print(min(t) / loops * 1e6, max(t) / loops * 1e6)  # usec
# create_unicode_buffer: 4.4 - 5.8 usec, 3.6 - 4.0 usec
# global result: 3.1 - 3.2 usec per loop
# return PyObject: 10.6 - 11.2 usec per loop
