LoadPython() {
    ; Try loading Python DLL from the path set in the PYTHONDLL environment
    ; variable. The variable is normally set by launcher.py.
    EnvGet, python_dll, PYTHONDLL
    if (python_dll) {
        HPYTHON_DLL := LoadLibraryEx(python_dll, LOAD_WITH_ALTERED_SEARCH_PATH)
        if (HPYTHON_DLL != NULL) {
            return HPYTHON_DLL
        }
        if (A_LastError != ERROR_MOD_NOT_FOUND) {
            End("Cannot load Python DLL: " A_LastError)
        }
    }

    ; Try default search-order. This approach works with virtualenv since
    ; activating one adds "VIRTUAL_ENV\Scripts" to the PATH.
    ; FIXME: venv doesn't create a python3.dll wrapper. Add support for venv.
    python_dll := "python3.dll"
    HPYTHON_DLL := LoadLibraryEx(python_dll)
    if (HPYTHON_DLL != NULL) {
        return HPYTHON_DLL
    }
    if (A_LastError != ERROR_MOD_NOT_FOUND) {
        End("Cannot load Python DLL: " A_LastError)
    }

    ; Try py.exe.
    arch := A_PtrSize * 8
    cmd := "py.exe -3-" arch " -c ""import os, sys; print(os.path.dirname(sys.executable), end='')"""
    pythonDir := StdoutToVar_CreateProcess(cmd)
    exists := FileExist(pythonDir)
    if (pythonDir != "" and FileExist(pythonDir) == "D") {
        python_dll := pythonDir "\python3.dll"
        HPYTHON_DLL := LoadLibraryEx(python_dll, LOAD_WITH_ALTERED_SEARCH_PATH)
        if (HPYTHON_DLL != NULL) {
            return HPYTHON_DLL
        }
    }
    if (A_LastError != ERROR_MOD_NOT_FOUND) {
        End("Cannot load Python DLL: " A_LastError)
    }

    End("Cannot find Python DLL.")
}

LoadLibraryEx(libFileName, flags:=0) {
    file := NULL
    return DllCall("LoadLibraryEx"
        , "Str", libFileName
        , "Ptr", file
        , "Int", flags
        , "Ptr")
}

PythonDllCall(function, args*) {
    if (HPYTHON_DLL) {
        return DllCall(CachedProcAddress(function), args*)
    }
}

CachedProcAddress(symbol, returnType:="Ptr") {
    proc := PYTHON_DLL_PROCS[symbol]
    if (not proc) {
        proc := DllCall("GetProcAddress", "Ptr", HPYTHON_DLL, "AStr", symbol, returnType)
        if (not proc) {
            throw Exception("Cannot get the address of " symbol " symbol. Error " A_LastError)
        }
        PYTHON_DLL_PROCS[symbol] := proc
    }
    return proc
}

Py_Initialize() {
    ; void Py_Initialize()
    PythonDllCall("Py_Initialize", "Cdecl")
}

Py_BuildValue(format) {
    ; PyObject* Py_BuildValue(const char *format, ...)
    ; Return value: New reference.
    return PythonDllCall("Py_BuildValue", "AStr", format, "Cdecl Ptr")
}

Py_FinalizeEx() {
    ; int Py_FinalizeEx()
    return PythonDllCall("Py_FinalizeEx", "Cdecl Int")
}

Py_IncRef(pyObject) {
    ; void Py_IncRef(PyObject *o)
    PythonDllCall("Py_IncRef", "Ptr", pyObject, "Cdecl")
}

Py_XIncRef(pyObject) {
    if (pyObject != NULL) {
        Py_IncRef(pyObject)
    }
}

Py_DecRef(pyObject) {
    ; void Py_DecRef(PyObject *o)
    PythonDllCall("Py_DecRef", "Ptr", pyObject, "Cdecl")
}

Py_XDecRef(pyObject) {
    if (pyObject != NULL) {
        Py_DecRef(pyObject)
    }
}

Py_TYPE(ob) {
    ; #define Py_TYPE(ob) (_PyObject_CAST(ob)->ob_type)
    ; #define _PyObject_CAST(op) ((PyObject*)(op))

    ; obRefcnt := NumGet(ob, "Ptr") ; Py_ssize_t
    return NumGet(ob + A_PtrSize, "UPtr")
}

PyDict_New() {
    ; PyObject* PyDict_New()
    ; Return value: New reference.
    return PythonDllCall("PyDict_New", "Cdecl Ptr")
}

PyDict_SetItem(p, key, val) {
    ; int PyDict_SetItem(PyObject *p, PyObject *key, PyObject *val)
    return PythonDllCall("PyDict_SetItem", "Ptr", p, "Ptr", key, "Ptr", val, "Cdecl Int")
}

PyFloat_AsDouble(pyfloat) {
    ; double PyFloat_AsDouble(PyObject *pyfloat)
    return PythonDllCall("PyFloat_AsDouble", "Ptr", pyfloat, "Cdecl Double")
}

PyFloat_FromDouble(value) {
    ; PyObject* PyFloat_FromDouble(double v)
    ; Return value: New reference.
    return PythonDllCall("PyFloat_FromDouble", "Double", value, "Cdecl Ptr")
}

PyFloat_Check(o) {
    PyFloat_Type := CachedProcAddress("PyFloat_Type")
    return PyObject_TypeCheck(o, PyFloat_Type)
}

PyGILState_Ensure() {
    ; PyGILState_STATE PyGILState_Ensure()
    return PythonDllCall("PyGILState_Ensure", "Cdecl Int")
}

PyGILState_Release(gstate) {
    ; void PyGILState_Release(PyGILState_STATE)
    PythonDllCall("PyGILState_Release", "Int", gstate, "Cdecl")
}

PyImport_AppendInittab(name, initfunc) {
    ; int PyImport_AppendInittab(const char *name, PyObject* (*initfunc)(void))
    return PythonDllCall("PyImport_AppendInittab"
        , "Ptr", name
        , "Ptr", RegisterCallback(initfunc, "C", 0)
        , "Cdecl Int")
}

PyImport_ImportModule(name) {
    ; PyObject* PyImport_ImportModule(const char *name)
    ; Return value: New reference.
    return PythonDllCall("PyImport_ImportModule", "AStr", name, "Cdecl Ptr")
}

PyMem_Free(p) {
    ; void PyMem_Free(void *p)
    return PythonDllCall("PyMem_Free", "Ptr", p, "Cdecl")
}

PyModule_Create2(module, apiVersion) {
    ; PyObject* PyModule_Create2(PyModuleDef *def, int module_api_version)
    ; Return value: New reference.
    return PythonDllCall("PyModule_Create2"
        , "Ptr", module
        , "Int", apiVersion
        , "Cdecl Ptr")
}

PyModule_AddObject(module, name, value) {
    ; int PyModule_AddObject(PyObject *module, const char *name, PyObject *value)
    return PythonDllCall("PyModule_AddObject"
        , "Ptr", module
        , "AStr", name
        , "Ptr", value
        , "Cdecl Int")
}

PyCallable_Check(pyObject) {
    ; int PyCallable_Check(PyObject *o)
    return PythonDllCall("PyCallable_Check", "Ptr", pyObject, "Cdecl Int")
}

PyContext_Copy(ctx) {
    ; PyObject *PyContext_Copy(PyObject *ctx)
    ; Return value: New reference.
    return PythonDllCall("PyContext_Copy", "Ptr", ctx, "Cdecl Ptr")
}

PyContext_CopyCurrent() {
    ; PyObject *PyContext_CopyCurrent(void)
    ; Return value: New reference.
    return PythonDllCall("PyContext_CopyCurrent", "Cdecl Ptr")
}

PyContext_Enter(ctx) {
    ; int PyContext_Enter(PyObject *ctx)
    return PythonDllCall("PyContext_Enter", "Ptr", ctx, "Cdecl Ptr")
}

PyContext_Exit(ctx) {
    ; int PyContext_Exit(PyObject *ctx)
    return PythonDllCall("PyContext_Exit", "Ptr", ctx, "Cdecl Ptr")
}

PyErr_CheckSignals() {
    ; int PyErr_CheckSignals()
    return PythonDllCall("PyErr_CheckSignals", "Cdecl Ptr")
}

PyErr_Clear() {
    ; void PyErr_Clear()
    PythonDllCall("PyErr_Clear", "Cdecl")
}

PyErr_ExceptionMatches(exc) {
    ; int PyErr_ExceptionMatches(PyObject *exc)
    return PythonDllCall("PyErr_ExceptionMatches", "Ptr", exc, "Cdecl Int")
}

PyErr_Fetch(ByRef ptype, ByRef pvalue, ByRef ptraceback) {
    ; PyErr_Fetch(PyObject **ptype, PyObject **pvalue, PyObject **ptraceback)
    PythonDllCall("PyErr_Fetch", "Ptr", &ptype, "Ptr", &pvalue, "Ptr", &ptraceback, "Cdecl")
    ptype := NumGet(ptype)
    pvalue := NumGet(pvalue)
    ptraceback := NumGet(ptraceback)
}

PyErr_NewException(name, base, dict) {
    ; PyObject* PyErr_NewException(const char *name, PyObject *base, PyObject *dict)
    ; Return value: New reference.
    return PythonDllCall("PyErr_NewException"
        , "AStr", name
        , "Ptr", base
        , "Ptr", dict
        , "Cdecl Ptr")
}

PyErr_Occurred() {
    ; PyObject* PyErr_Occurred()
    ; Return value: Borrowed reference.
    return PythonDllCall("PyErr_Occurred", "Cdecl Ptr")
}

PyErr_Print() {
    ; void PyErr_Print()
    PythonDllCall("PyErr_Print", "Cdecl")
}

PyErr_Restore(ptype, pvalue, ptraceback) {
    ; void PyErr_Restore(PyObject *type, PyObject *value, PyObject *traceback)
    PythonDllCall("PyErr_Restore", "Ptr", ptype, "Ptr", pvalue, "Ptr", ptraceback, "Cdecl")
}

PyErr_SetObject(type, value) {
    ; void PyErr_SetObject(PyObject *type, PyObject *value)
    PythonDllCall("PyErr_SetObject", "Ptr", type, "Ptr", value, "Cdecl")
}

PyErr_SetString(type, message) {
    ; void PyErr_SetString(PyObject *type, const char *message)
    encoded := EncodeString(message)
    PythonDllCall("PyErr_SetString", "Ptr", type, "Ptr", &encoded, "Cdecl")
}

PyEval_RestoreThread(save) {
    ; void PyEval_RestoreThread(PyThreadState *tstate)
    PythonDllCall("PyEval_RestoreThread", "Ptr", save, "Cdecl")
}

PyEval_SaveThread() {
    ; PyThreadState* PyEval_SaveThread()
    return PythonDllCall("PyEval_SaveThread", "Cdecl Ptr")
}

PyExceptionInstance_Check(o) {
    return PyType_FastSubclass(Py_TYPE(o), Py_TPFLAGS_BASE_EXC_SUBCLASS)
}

PyLong_AsLongLong(obj) {
    ; long long PyLong_AsLongLong(PyObject *obj)
    return PythonDllCall("PyLong_AsLongLong", "Ptr", obj, "Cdecl Int64")
}

PyLong_Check(o) {
    return PyType_FastSubclass(Py_TYPE(o), Py_TPFLAGS_LONG_SUBCLASS)
}

PyLong_FromLongLong(value) {
    ; PyObject* PyLong_FromLongLong(long long v)
    ; Return value: New reference.
    return PythonDllCall("PyLong_FromLongLong", "Int64", value, "Cdecl Ptr")
}

PyObject_GetAttrString(obj, attr) {
    ; PyObject* PyObject_GetAttrString(PyObject *o, const char *attr_name)
    ; Return value: New reference.
    return PythonDllCall("PyObject_GetAttrString", "Ptr", obj, "AStr", attr, "Cdecl Ptr")
}

PyObject_CallObject(pyObject, args) {
    ; PyObject* PyObject_CallObject(PyObject *callable, PyObject *args)
    ; Return value: New reference.
    return PythonDllCall("PyObject_CallObject", "Ptr", pyObject, "Ptr", args, "Cdecl Ptr")
}

PyObject_Repr(o) {
    ; PyObject* PyObject_Repr(PyObject *o)
    ; Return value: New reference.
    return PythonDllCall("PyObject_Repr", "Ptr", o, "Cdecl Ptr")
}

PyObject_SetAttrString(obj, attr, v) {
    ; int PyObject_SetAttrString(PyObject *o, const char *attr_name, PyObject *v)
    return PythonDllCall("PyObject_SetAttrString", "Ptr", obj, "AStr", attr, "Ptr", v, "Cdecl Ptr")
}

PyObject_TypeCheck(ob, tp) {
    obType := Py_TYPE(ob)
    return obType == tp or PyType_IsSubtype(obType, tp)
}

PyTuple_GetItem(p, pos) {
    ; PyObject* PyTuple_GetItem(PyObject *p, Py_ssize_t pos)
    ; Return value: Borrowed reference.
    return PythonDllCall("PyTuple_GetItem", "Ptr", p, "Ptr", pos, "Cdecl Ptr")
}

PyTuple_New(len) {
    ; PyObject* PyTuple_New(Py_ssize_t len)
    ; Return value: New reference.
    return PythonDllCall("PyTuple_New", "Ptr", len, "Cdecl Ptr")
}

PyTuple_SetItem(p, pos, o) {
    ; int PyTuple_SetItem(PyObject *p, Py_ssize_t pos, PyObject *o)
    return PythonDllCall("PyTuple_SetItem", "Ptr", p, "Ptr", pos, "Ptr", o, "Cdecl Int")
}

PySys_SetArgvEx(argc, argv, updatepath:=1) {
    ; void PySys_SetArgvEx(int argc, wchar_t **argv, int updatepath)
    PythonDllCall("PySys_SetArgvEx", "Int", argc, "Ptr", argv, "Int", updatepath, "Cdecl")
}

PySys_SetPath(path) {
    ; void PySys_SetPath(const wchar_t *path)
    PythonDllCall("PySys_SetPath", "Str", path, "Cdecl")
}

PyTuple_Pack(n, objects*) {
    ; PyObject* PyTuple_Pack(Py_ssize_t n, ...)
    ; Return value: New reference.
    dllArgs := []
    for _, obj in objects {
        dllArgs.Push("Ptr")
        dllArgs.Push(obj)
    }
    dllArgs.Push("Cdecl Ptr")
    return PythonDllCall("PyTuple_Pack", "Ptr", n, dllArgs*)
}

PyTuple_Size(p) {
    ; Py_ssize_t PyTuple_Size(PyObject *p)
    return PythonDllCall("PyTuple_Size", "Ptr", p, "Cdecl Ptr")
}

PyType_FastSubclass(t, f) {
    ; #define PyType_FastSubclass(t,f)  PyType_HasFeature(t,f)
    ; #define PyType_HasFeature(t,f)  ((PyType_GetFlags(t) & (f)) != 0)

    flags := PythonDllCall("PyType_GetFlags", "Ptr", t, "Cdecl UInt")
    return flags & f != 0
}

PyType_IsSubtype(a, b) {
    ; int PyType_IsSubtype(PyTypeObject *a, PyTypeObject *b)
    return PythonDllCall("PyType_IsSubtype", "Ptr", a, "Ptr", b, "Cdecl Int")
}

PyUnicode_AsWideCharString(unicode) {
    ; wchar_t* PyUnicode_AsWideCharString(PyObject *unicode, Py_ssize_t *size)
    size := 0
    wchars := PythonDllCall("PyUnicode_AsWideCharString", "Ptr", unicode, "Ptr", &size, "Cdecl Ptr")
    if (wchars == NULL) {
        throw Exception("cannot convert Python unicode to AHK string.")
    }
    size := NumGet(size)
    result := StrGet(wchars, size)
    PyMem_Free(wchars)
    return result
}

PyUnicode_Check(o) {
    ; int PyUnicode_Check(PyObject *o)
    return PyType_FastSubclass(Py_TYPE(o), Py_TPFLAGS_UNICODE_SUBCLASS)
}

PyUnicode_InternFromString(string) {
    ; PyObject* PyUnicode_InternFromString(const char *v)
    ; Return value: New reference.
    return PythonDllCall("PyUnicode_InternFromString", "Ptr", string, "Cdecl Ptr")
}

PyUnicode_FromString(string) {
    ; PyObject *PyUnicode_FromString(const char *u)
    ; Return value: New reference.
    encoded := EncodeString(string)
    return PythonDllCall("PyUnicode_FromString", "Ptr", &encoded, "Cdecl Ptr")
}
