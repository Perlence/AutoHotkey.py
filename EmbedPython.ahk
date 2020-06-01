#NoEnv
#Warn, All, MsgBox

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
global BOUND_TRIGGERS := {}

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
    EnvGet, venv, VIRTUAL_ENV
    if (venv != "") {
        EnvSet, PYTHONHOME, %venv%
    }

    LoadPython()
    PackBuiltinModule()

    Critical, On
    PyImport_AppendInittab(&AHKModule_name, Func("PyInit_ahk"))
    Py_Initialize()

    Py_None := Py_BuildValue("")

    argv0 := A_ScriptFullPath
    packArgs := ["Ptr", &argv0]
    for i, arg in A_Args {
        packArgs.Push("Ptr")
        packArgs.Push(A_Args.GetAddress(i))
    }
    argc := A_Args.Length() + 1
    Pack(argv, packArgs*)
    PySys_SetArgv(argc, &argv)

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
    Critical, Off
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
    wasCritical := A_IsCritical
    Critical, On
    gstate := PyGILState_Ensure()

    ; AHK debugger doesn't see local variables in a C callback function. Call a
    ; regular AHK function.
    result := _AHKCall(self, args)

    PyGILState_Release(gstate)
    if (wasCritical == 0) {
        Critical, Off
    }

    return result
}

_AHKCall(self, args) {
    pyFunc := PyTuple_GetItem(args, 0)
    if (pyFunc == NULL) {
        TypeError := CachedProcAddress("PyExc_TypeError", "PtrP")
        PyErr_SetString(TypeError, "_ahk.call() missing 1 required positional argument: 'func'")
        return NULL
    }

    func := PythonToAHK(pyFunc)

    funcRef := Func(func)
    if (not funcRef) {
        ; Try custom command wrapper.
        funcRef := Func("_" func)
    }
    if (not funcRef) {
        PyErr_SetString(Py_AHKError, "unknown function " func)
        return NULL
    }

    ; Parse the arguments.
    ahkArgs := []
    i := 1
    size := PyTuple_Size(args)
    while (i < size) {
        arg := PyTuple_GetItem(args, i)
        if (arg == Py_None) {
            ; Ignore all arguments after None.
            break
        }
        try {
            ahkArg := PythonToAHK(arg)
        } catch e {
            PyErr_SetAHKError(e)
            return NULL
        }
        if (PyErr_Occurred()) {
            ; Python couldn't convert the value, e.g. OverflowError.
            return NULL
        }
        ahkArgs.Push(ahkArg)
        i += 1
    }

    if (func == "Sleep") {
        ; Release the GIL and let AHK process its message queue.
        save := PyEval_SaveThread()
        Critical, Off
    }
    try {
        result := %funcRef%(ahkArgs*)
    } catch e {
        PyErr_SetAHKError(e)
        return NULL
    } finally {
        if (func == "Sleep") {
            Critical, On
            PyEval_RestoreThread(save)
        }
    }

    return AHKToPython(result)
}

AHKToPython(value) {
    if (IsObject(value)) {
        ; TODO: Convert AHK object to Python dict.
        NotImplementedError := CachedProcAddress("PyExc_NotImplementedError", "PtrP")
        PyErr_SetString(NotImplementedError, "cannot convert AHK object to Python value")
        return NULL
    } else if (value == "") {
        if (Py_EmptyString == NULL) {
            Py_EmptyString := PyUnicode_InternFromString(&EMPTY_STRING)
        }
        return Py_EmptyString
    } else if value is integer
        return PyLong_FromLongLong(value)
    else if value is float
        return PyFloat_FromDouble(value)
    else {
        ; The value is a string.
        return PyUnicode_FromString(value)
    }
}

PythonToAHK(pyObject, borrowed:=True) {
    ; TODO: Convert dicts to objects and lists to arrays.
    if (PyUnicode_Check(pyObject)) {
        return PyUnicode_AsWideCharString(pyObject)
    } else if (PyLong_Check(pyObject)) {
        return PyLong_AsLongLong(pyObject)
    } else if (PyFloat_Check(pyObject)) {
        return PyFloat_AsDouble(pyObject)
    } else if (PyCallable_Check(pyObject)) {
        if (borrowed) {
            Py_IncRef(pyObject)
        }
        CALLBACKS[pyObject] := pyObject
        boundFunc := BOUND_TRIGGERS[pyObject]
        if (not boundFunc) {
            boundFunc := Func("Trigger").Bind(pyObject)
            BOUND_TRIGGERS[pyObject] := boundFunc
        }
        return boundFunc
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

EncodeString(string) {
    ; Convert a UTF-16 string to a UTF-8 one.
    len := StrPut(string, "utf-8")
    VarSetCapacity(var, len)
    StrPut(string, &var, "utf-8")
    return var
}

Trigger(key, args*) {
    funcObjPtr := CALLBACKS[key]
    if (not funcObjPtr) {
        return
    }

    wasCritical := A_IsCritical
    Critical, On
    gstate := PyGILState_Ensure()

    argsPtr := NULL
    result := PyObject_CallObject(funcObjPtr, argsPtr)
    if (result == "") {
        End("Call to '" key "' callback failed: " ErrorLevel)
    } else if (result == NULL) {
        PrintErrorOrExit()
    }
    Py_DecRef(result)

    PyGILState_Release(gstate)
    if (wasCritical == 0) {
        Critical, Off
    }
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
    ; TODO: Consider replacing some of End invocations with raising Python
    ; exceptions.
    message .= "`nThe application will now exit."
    MsgBox, % message
    ExitApp
}

GuiContextMenu:
GuiDropFiles:
GuiEscape:
GuiSize:
OnClipboardChange:
    Trigger(A_ThisLabel)
    return

GuiClose:
    OnExitFunc("Close", 0, A_ThisLabel)
    return

OnExitFunc(reason, code, label:="OnExit") {
    if (Trigger(label) == 0) {
        return
    }
    if (Py_FinalizeEx() < 0) {
        code := 120
    }
    ExitApp, %code%
}

OnMessageClosure(wParam, lParam, msg, hwnd) {
    Trigger("OnMessage " . msg, wParam, lParam, msg, hwnd)
}
