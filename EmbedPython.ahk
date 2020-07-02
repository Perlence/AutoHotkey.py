#NoEnv
#Warn, All, MsgBox
SendMode, Input
SetBatchLines, -1

global NULL := 0
global EMPTY_STRING := ""

global LOAD_WITH_ALTERED_SEARCH_PATH := 0x8
global ERROR_MOD_NOT_FOUND := 0x7e
global HPYTHON_DLL := NULL
global PYTHON_DLL_PROCS := {}

; Python constants
global METH_VARARGS := 0x0001
global PYTHON_API_VERSION := 1013
global Py_TPFLAGS_LONG_SUBCLASS := 1 << 24
global Py_TPFLAGS_UNICODE_SUBCLASS := 1 << 28
global Py_TPFLAGS_BASE_EXC_SUBCLASS := 1 << 30

global CALLBACKS := {}
global WRAPPED_PYTHON_FUNCTIONS := {}

global AHKMethods
global AHKModule
global AHKModule_name

; Live Python objects
global Py_None := NULL
global Py_EmptyString := NULL
global Py_AHKError := NULL
global Py_HandleSystemExit := NULL

OnExit("OnExitFunc")

Main()

; END AUTO-EXECUTE SECTION
return


#Include, <StdoutToVar_CreateProcess>
#Include, <PythonDll>
#Include, <Commands>


Main() {
    ; EnvSet command is not respected by C getenv, do it via ucrtbase.
    DllCall("ucrtbase\_putenv_s", "AStr", "PYTHONUNBUFFERED", "AStr", "1", "Int")

    LoadPython()
    PackBuiltinModule()

    PyImport_AppendInittab(&AHKModule_name, Func("PyInit_ahk"))
    Py_Initialize()

    Py_None := Py_BuildValue("")

    argv0 := A_ScriptFullPath
    packArgs := ["Ptr", &argv0]
    argStr := argv0
    for i, arg in A_Args {
        packArgs.Push("Ptr")
        packArgs.Push(A_Args.GetAddress(i))
        argStr := argStr " " arg
    }
    argc := A_Args.Length() + 1
    Pack(argv, packArgs*)
    PySys_SetArgv(argc, &argv)

    DetectHiddenWindows, On
    WinSetTitle, ahk_id %A_ScriptHwnd%, , % argStr " - AutoHotkey v" A_AhkVersion
    DetectHiddenWindows, Off

    ; Import the higher-level ahk module to bootstrap the excepthook.
    mainModule := PyImport_ImportModule("ahk.main")
    if (mainModule == NULL) {
        End("Cannot load ahk module.")
    }

    Py_AHKError := PyObject_GetAttrString(mainModule, "Error")
    if (Py_AHKError == NULL) {
        Py_DecRef(mainModule)
        End("Module 'main' has no attribute 'Error'.")
    }

    Py_HandleSystemExit := PyObject_GetAttrString(mainModule, "handle_system_exit")
    if (Py_HandleSystemExit == NULL) {
        Py_DecRef(mainModule)
        End("Module 'main' has no attribute 'handle_system_exit'.")
    }

    mainFunc := PyObject_GetAttrString(mainModule, "main")
    if (mainFunc == NULL) {
        Py_DecRef(mainModule)
        End("Module 'main' has no attribute 'main'.")
    }

    Py_DecRef(mainModule)

    result := PyObject_CallObject(mainFunc, NULL)
    Py_DecRef(mainFunc)
    ; TODO: Handle SIGTERM gracefully.
    if (result == NULL) {
        PrintErrorOrExit()
    }
    Py_DecRef(result)
}

PackBuiltinModule() {
    PackBuiltinMethods()

    ; typedef struct PyModuleDef{
    ;   PyModuleDef_Base m_base;
    ;   const char* m_name;
    ;   const char* m_doc;
    ;   Py_ssize_t m_size;
    ;   PyMethodDef *m_methods;
    ;   struct PyModuleDef_Slot* m_slots;
    ;   traverseproc m_traverse;
    ;   inquiry m_clear;
    ;   freefunc m_free;
    ; } PyModuleDef;

    ; static PyModuleDef AHKModule = {
    ;     PyModuleDef_HEAD_INIT, "ahk", NULL, -1, AHKMethods,
    ;     NULL, NULL, NULL, NULL
    ; };

    global AHKModule_name := EncodeString("_ahk")
    global AHKModule
    Pack(AHKModule
        , "Int64", 1  ; ob_refcnt
        , "Ptr", NULL ; ob_type
        , "Ptr", NULL ; m_init
        , "Int64", 0  ; m_index
        , "Ptr", NULL ; m_copy
        , "Ptr", &AHKModule_name
        , "Ptr", NULL
        , "Int64", -1
        , "Ptr", &AHKMethods
        , "Ptr", NULL
        , "Ptr", NULL
        , "Ptr", NULL
        , "Ptr", NULL)
}

PackBuiltinMethods() {
    ; struct PyMethodDef {
    ;     const char  *ml_name;
    ;     PyCFunction ml_meth;
    ;     int         ml_flags;
    ;     const char  *ml_doc;
    ; };

    ; static PyMethodDef AHKMethods[] = {
    ;     {"call", AHKCall, METH_VARARGS,
    ;      "docstring blablabla"},
    ;     {NULL, NULL, 0, NULL} // sentinel
    ; };

    global AHKMethod_call_name := EncodeString("call")
    global AHKMethod_call_doc := EncodeString("Execute the given AutoHotkey function.")

    global AHKMethods
    Pack(AHKMethods
        ; -- call
        , "Ptr", &AHKMethod_call_name
        ; Register a Fast callback -- don't run it in a new AHK thread. Python
        ; code must be able to change AHK's "thread-local" parameters, e.g.
        ; SendLevel.
        , "Ptr", RegisterCallback("AHKCall", "C Fast", 2)
        , "Int64", METH_VARARGS
        , "Ptr", &AHKMethod_call_doc

        ; -- sentinel
        , "Ptr", NULL
        , "Ptr", NULL
        , "Int64", 0
        , "Ptr", NULL)
}

Pack(ByRef var, args*) {
    static typeSizes := {Char: 1, UChar: 1
        , Short: 2, UShort: 2
        , Int: 4 , UInt: 4, Int64: 8
        , Float: 4, Double: 8
        , Ptr: A_PtrSize, UPtr: A_PtrSize}

    cap := 0
    typedValues := []
    typedValue := {}
    for index, param in args {
        if (Mod(index, 2) == 1) {
            ; Type string.
            size := typeSizes[param]
            if (not size) {
                End("Invalid type " param)
            }
            cap += size
            typedValue.Type := param
            typedValue.Size := size
        } else {
            typedValue.Value := param
            typedValues.Push(typedValue)
            typedValue := {}
        }
    }

    VarSetCapacity(var, cap, 0)
    offset := 0
    for index, tv in typedValues {
        NumPut(tv.Value, var, offset, tv.Type)
        offset += tv.Size
    }
}

PyInit_ahk() {
    return PyModule_Create2(&AHKModule, PYTHON_API_VERSION)
}

AHKCall(self, args) {
    gstate := PyGILState_Ensure()
    try {
        ; AHK debugger doesn't see local variables in a C callback function. Call a
        ; regular AHK function.
        result := _AHKCall(self, args)
    } finally {
        PyGILState_Release(gstate)
    }
    return result
}

_AHKCall(self, args) {
    pyFuncName := PyTuple_GetItem(args, 0)
    if (pyFuncName == NULL) {
        TypeError := CachedProcAddress("PyExc_TypeError", "PtrP")
        PyErr_SetString(TypeError, "_ahk.call() missing 1 required positional argument: 'func'")
        return NULL
    }

    func := PythonToAHK(pyFuncName)

    funcRef := Func(func)
    if (not funcRef) {
        ; Try custom command wrapper.
        funcRef := Func("_" func)
    }
    if (not funcRef) {
        PyErr_SetString(Py_AHKError, "unknown function " func)
        return NULL
    }

    ahkArgs := PythonArgsToAHK(args)
    if (ahkArgs == "") {
        return NULL
    }

    ; Release the GIL and let AHK process its message queue.
    save := PyEval_SaveThread()
    try {
        result := %funcRef%(ahkArgs*)
    } catch e {
        PyEval_RestoreThread(save)
        FreeWrappedFunctions()
        PyErr_SetAHKError(e)
        return NULL
    }
    PyEval_RestoreThread(save)
    FreeWrappedFunctions()

    return AHKToPython(result)
}

PythonArgsToAHK(pyArgs) {
    ; Parse the arguments.
    ahkArgs := []
    i := 1
    size := PyTuple_Size(pyArgs)
    while (i < size) {
        arg := PyTuple_GetItem(pyArgs, i)
        if (arg == Py_None) {
            ; Ignore all arguments after None.
            break
        }
        try {
            ahkArg := PythonToAHK(arg)
        } catch e {
            PyErr_SetAHKError(e)
            return
        }
        if (PyErr_Occurred()) {
            ; Python couldn't convert the value, e.g. OverflowError.
            return
        }
        ahkArgs.Push(ahkArg)
        i += 1
    }
    return ahkArgs
}

PythonToAHK(pyObject, borrowed:=True) {
    ; TODO: Convert dicts to objects and lists to arrays.
    if (pyObject == Py_None) {
        return ""
    } else if (PyUnicode_Check(pyObject)) {
        return PyUnicode_AsWideCharString(pyObject)
    } else if (PyLong_Check(pyObject)) {
        return PyLong_AsLongLong(pyObject)
    } else if (PyFloat_Check(pyObject)) {
        return PyFloat_AsDouble(pyObject)
    } else if (PyCallable_Check(pyObject)) {
        ahkFunc := WRAPPED_PYTHON_FUNCTIONS[pyObject]
        if (not ahkFunc) {
            if (borrowed) {
                Py_IncRef(pyObject)
            }
            ahkFunc := new WrappedPythonFunction(pyObject)
            WRAPPED_PYTHON_FUNCTIONS[pyObject] := ahkFunc
        }
        ; TODO: Pass A_ThisHotkey to hotkey callback.
        return ahkFunc
    } else {
        pyRepr := PyObject_Repr(pyObject)
        if (PyUnicode_Check(pyRepr)) {
            repr := PyUnicode_AsWideCharString(pyRepr)
            Py_DecRef(pyRepr)
            throw Exception("cannot convert '" repr "' to an AHK value")
        } else {
            Py_DecRef(pyRepr)
            throw Exception("cannot convert Python object to an AHK value")
        }
    }
}

class WrappedPythonFunction {
    __New(pyFunc) {
        this.pyFunc := pyFunc
    }

    __Call(method, args*) {
        return PyCall(this.pyFunc, args*)
    }
}

FreeWrappedFunctions() {
    for pyFunc, value in WRAPPED_PYTHON_FUNCTIONS {
        if (value == "FREE") {
            WRAPPED_PYTHON_FUNCTIONS.Delete(pyFunc)
            Py_DecRef(pyFunc)
        }
    }
}

AHKToPython(value) {
    if (IsObject(value)) {
        ; TODO: Should this be a Python wrapper around "value" and not a copy?
        result := PyDict_New()
        for k, v in value {
            pyKey := AHKToPython(k)
            pyValue := AHKToPython(v)
            set := PyDict_SetItem(result, pyKey, pyValue)
            if (set < 0) {
                return NULL
            }
        }
        return result
    } else if (value == "") {
        if (Py_EmptyString == NULL) {
            Py_EmptyString := PyUnicode_InternFromString(&EMPTY_STRING)
        }
        Py_IncRef(Py_EmptyString)
        return Py_EmptyString
    } else if value is integer
        ; TODO: AHK integers are strings, consider returning them as such.
        return PyLong_FromLongLong(value)
    else if value is float
        return PyFloat_FromDouble(value)
    else {
        ; The value is a string.
        return PyUnicode_FromString(value)
    }
}

PyErr_SetAHKError(err) {
    tup := PyTuple_Pack(5
        , AHKToPython(err.Message)
        , AHKToPython(err.What)
        , AHKToPython(err.Extra)
        , AHKToPython(err.File)
        , AHKToPython(err.Line))
    if (tup == NULL) {
        PyErr_SetString(Py_AHKError, err.Message)
        return
    }
    PyErr_SetObject(Py_AHKError, tup)
    Py_DecRef(tup)
}

PyCall(pyFunc, args*) {
    if (not pyFunc) {
        return
    }

    gstate := PyGILState_Ensure()
    try {
        err := PyErr_Occurred()
        if (err != NULL) {
            ; An unhandled error has happened before callback was invoked by
            ; AHK, do nothing.
            return
        }
        pyArgs := AHKArgsToPython(args)
        result := ""
        pyResult := PyObject_CallObject(pyFunc, pyArgs)
        Py_XDecRef(pyArgs)
        if (pyResult == "") {
            pyRepr := PyObject_Repr(pyFunc)
            if (PyUnicode_Check(pyRepr)) {
                repr := PyUnicode_AsWideCharString(pyRepr)
                Py_DecRef(pyRepr)
                throw Exception("Call to '" repr "' failed: " ErrorLevel)
            } else {
                Py_DecRef(pyRepr)
                throw Exception("Call to a Python function failed: " ErrorLevel)
            }
        } else if (pyResult == NULL) {
            PrintErrorOrExit()
        } else {
            result := PythonToAHK(pyResult, False)
            Py_DecRef(pyResult)
        }
    } finally {
        PyGILState_Release(gstate)
    }

    return result
}

AHKArgsToPython(ahkArgs) {
    if (ahkArgs.Count() == 0) {
        return NULL ; Not an error, just no args
    }

    pyArgs := PyTuple_New(ahkArgs.Count())
    if (pyArgs == NULL) {
        throw Exception("Couldn't create argument tuple to call Python function")
    }
    for i, arg in ahkArgs {
        PyTuple_SetItem(pyArgs, i-1, AHKToPython(arg))
    }
    return pyArgs
}

EncodeString(string) {
    ; Convert a UTF-16 string to a UTF-8 one.
    len := StrPut(string, "utf-8")
    VarSetCapacity(var, len)
    StrPut(string, &var, "utf-8")
    return var
}

PrintErrorOrExit() {
    PyExc_SystemExit := CachedProcAddress("PyExc_SystemExit", "PtrP")
    if (!PyErr_ExceptionMatches(PyExc_SystemExit)) {
        PyErr_Print()
        return
    }

    type := NULL
    value := NULL
    tb := NULL
    PyErr_Fetch(type, value, tb)

    args := PyTuple_Pack(1, value)
    if (args == NULL) {
        PyErr_Print()
        return
    }

    pyExitCode := PyObject_CallObject(Py_HandleSystemExit, args)
    Py_DecRef(args)
    if (pyExitCode == NULL) {
        ; Something happened during handle_system_exit.
        PyErr_Print()
        return
    }

    exitCode := PythonToAHK(pyExitCode, False)
    Py_DecRef(pyExitCode)
    ExitApp, %exitCode%
}

End(message) {
    message .= "`nThe application will now exit."
    MsgBox, % message
    ExitApp
}

GuiContextMenu:
GuiDropFiles:
GuiEscape:
GuiSize:
OnClipboardChange:
    PyCall(CALLBACKS[A_ThisLabel])
    return

GuiClose:
    OnExitFunc("Close", 0, A_ThisLabel)
    return

OnExitFunc(reason, code, label:="OnExit") {
    if (PyCall(CALLBACKS[label]) == 0) {
        return
    }
    if (Py_FinalizeEx() < 0) {
        code := 120
    }
    ExitApp, %code%
}
