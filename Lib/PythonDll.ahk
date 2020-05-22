LoadPython() {  
    ; Try default search-order. This approach respects VIRTUAL_ENV as long as 
    ; "VIRTUAL_ENV\Scripts" is in the PATH.
    python_dll := "python3.dll"
    HPYTHON_DLL := LoadLibraryEx(python_dll)
    if (HPYTHON_DLL != NULL) {
        return HPYTHON_DLL
    }
    if (A_LastError != ERROR_MOD_NOT_FOUND) {
        End("Cannot load Python DLL: " A_LastError)
    }
    
    ; Try py.exe.
    cmd := "py.exe -3 -c ""import os, sys; print(os.path.dirname(sys.executable), end='')"""
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
    proc := PYTHON_DLL_PROCS[function]
    if (not proc) {
        proc := DllCall("GetProcAddress", "Ptr", HPYTHON_DLL, "AStr", function, "Ptr")
        if (not proc) {
            End("Cannot get the address of " function " function. Error " A_LastError)
        }
        PYTHON_DLL_PROCS[function] := proc
    }
    return DllCall(proc, args*)
}

Py_Initialize() {
    PythonDllCall("Py_Initialize", "Cdecl")
}

Py_Main(argc, argv) {
    return PythonDllCall("Py_Main", "Int", argc, "Ptr", argv, "Cdecl Int")
}

Py_BuildValue(format) {
    return PythonDllCall("Py_BuildValue", "AStr", format, "Cdecl Ptr")
}

Py_BuildNone() {
    if (PY_NONE == NULL) {
        PY_NONE := PythonDllCall("Py_BuildValue", "AStr", "", "Cdecl Ptr")
        if (PY_NONE == NULL) {
            End("Cannot build None")
        }
    }
    return PY_NONE
}

Py_IncRef(pyObject) {
    PythonDllCall("Py_IncRef", "Ptr", pyObject, "Cdecl")
}

Py_XIncRef(pyObject) {
    if (pyObject != NULL) {
        Py_IncRef(pyObject)
    }
}

Py_DecRef(pyObject) {
    PythonDllCall("Py_DecRef", "Ptr", pyObject, "Cdecl")
}

Py_XDecRef(pyObject) {
    if (pyObject != NULL) {
        Py_DecRef(pyObject)
    }
}

Py_Finalize() {
    PythonDllCall("Py_Finalize", "Cdecl")
}

PyImport_AppendInittab(name, initfunc) {
    return PythonDllCall("PyImport_AppendInittab"
        , "Ptr", name
        , "Ptr", initfunc
        , "Cdecl Int")
}

PyModule_Create2(module, api_version) {
    return PythonDllCall("PyModule_Create2"
        , "Ptr", module
        , "Int", api_version
        , "Cdecl Ptr")
}

PyModule_AddObject(module, name, value) {
    return PythonDllCall("PyModule_AddObject"
        , "Ptr", module
        , "AStr", name
        , "Ptr", value
        , "Cdecl Int")
}

PyArg_ParseTuple(args, format, dest*) {
    dllArgs := ["Ptr", args, "AStr", format]
    for _, arg in dest {
        dllArgs.Push("Ptr")
        dllArgs.Push(arg)
    }
    dllArgs.Push("Cdecl Int")
    return PythonDllCall("PyArg_ParseTuple", dllArgs*)
}

PyCallable_Check(pyObject) {
    return PythonDllCall("PyCallable_Check", "Ptr", pyObject, "Cdecl")
}

PyErr_NewException(name, base, dict) {
    return PythonDllCall("PyErr_NewException"
        , "AStr", name
        , "Ptr", base
        , "Ptr", dict
        , "Cdecl Ptr")
}

PyErr_SetString(exception, message) {
    encoded := EncodeString(message)
    PythonDllCall("PyErr_SetString", "Ptr", exception, "Ptr", &encoded)
}

PyErr_Print() {
    PythonDllCall("PyErr_Print", "Cdecl")
}

PyLong_FromLong(value) {
    return PythonDllCall("PyLong_FromLong", "Int", value, "Cdecl Ptr")
}

PyObject_CallObject(pyObject, args) {
    return PythonDllCall("PyObject_CallObject", "Ptr", pyObject, "Ptr", args, "Cdecl Ptr")
}

PyUnicode_InternFromString(string) {
    return PythonDllCall("PyUnicode_InternFromString", "Ptr", string, "Cdecl Ptr")
}

PyUnicode_FromString(string) {
    encoded := EncodeString(string)
    return PythonDllCall("PyUnicode_FromString", "Ptr", &encoded, "Cdecl Ptr")
}
