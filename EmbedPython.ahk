#NoEnv
#Warn, All, MsgBox

; TODO: Save the source as UTF-8 with BOM?

global NULL := 0
global ENCODING := "CP65001" ; UTF-8 code page
; TODO: Find Python DLL with py.exe or in VIRTUAL_ENV.
global PYTHON_DLL := "c:\Users\Sviatoslav\AppData\Local\Programs\Python\Python38\python38.dll"
global METH_VARARGS := 0x0001
global PYTHON_API_VERSION := 1013

global closures := {}

global EMPTY_STRING := ""

AHKCallCmd(self, args)
{
    ; const char *cmd;
    cmd := NULL
    ; Maximum number of AHK command arguments seems to be 11
    arg1 := NULL
    arg2 := NULL
    arg3 := NULL
    arg4 := NULL
    arg5 := NULL
    arg6 := NULL
    arg7 := NULL
    arg8 := NULL
    arg9 := NULL
    arg10 := NULL
    arg11 := NULL

    if (!DllCall(PYTHON_DLL "\PyArg_ParseTuple"
            , Ptr, args
            , AStr, "s|sssssssssss:call_cmd"
            , Ptr, &cmd
            , Ptr, &arg1
            , Ptr, &arg2
            , Ptr, &arg3
            , Ptr, &arg4
            , Ptr, &arg5
            , Ptr, &arg6
            , Ptr, &arg7
            , Ptr, &arg8
            , Ptr, &arg9
            , Ptr, &arg10
            , Ptr, &arg11
            , "Cdecl")) {
        return NULL
    }

    cmd := NumGet(cmd) ; Decode number from binary.
    cmd := StrGet(cmd, ENCODING) ; Read string from address `cmd`.

    Loop, 11
    {
        if (arg%A_Index% != NULL) {
            arg%A_Index% := NumGet(arg%A_Index%)
            arg%A_Index% := StrGet(arg%A_Index%, ENCODING)
        }
    }

    if (!Func("_" cmd)) {
        ; TODO: Raise Python exception.
        end("Unknown command " cmd)
        return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, 1, "Cdecl Ptr")
    }

    if (arg1 == NULL) {
        result := _%cmd%()
    } else if (arg2 == NULL) {
        result := _%cmd%(arg1)
    } else if (arg3 == NULL) {
        result := _%cmd%(arg1, arg2)
    } else if (arg4 == NULL) {
        result := _%cmd%(arg1, arg2, arg3)
    } else if (arg5 == NULL) {
        result := _%cmd%(arg1, arg2, arg3, arg4)
    } else if (arg6 == NULL) {
        result := _%cmd%(arg1, arg2, arg3, arg4, arg5)
    } else if (arg7 == NULL) {
        result := _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6)
    } else if (arg8 == NULL) {
        result := _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
    } else if (arg9 == NULL) {
        result := _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)
    } else if (arg10 == NULL) {
        result := _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9)
    } else if (arg11 == NULL) {
        result := _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10)
    } else {
        result := _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10, arg11)
    }

    return AHKToPython(result)
}

AHKToPython(value) {
    if (IsObject(value)) {
        ; TODO: Convert AHK object to Python dict.
        end("Not implemented")
    } else if (IsFunc(value)) {
        ; TODO: Wrap AHK function to be called from Python?
        end("Not implemented")
    } else if (value == "") {
        return DllCall(PYTHON_DLL "\PyUnicode_InternFromString", Ptr, &EMPTY_STRING, "Cdecl Ptr")
    } else if (value+0 == value) {
        ; The value is a number.
        return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, value, "Cdecl Ptr")
    } else {
        ; The value is a string.
        StrPutVar(value, encoded)
        return DllCall(PYTHON_DLL "\PyUnicode_FromString", Ptr, &encoded, "Cdecl Ptr")
    }
}

StrPutVar(string, ByRef var)
{
    VarSetCapacity(var, StrPut(string, ENCODING))
    return StrPut(string, &var, ENCODING)
}

; static PyMethodDef AHKMethods[] = {
;     {"call_cmd", AHKCallCmd, METH_VARARGS,
;      "docstring blablabla"},
;     {NULL, NULL, 0, NULL}
; };

StrPutVar("call_cmd", AHKMethod_call_cmd_name)
AHKMethod_call_cmd_meth := RegisterCallback("AHKCallCmd", "C")
AHKMethod_call_cmd_flags := METH_VARARGS
StrPutVar("Return the number of arguments received by the process.", AHKMethod_call_cmd_doc)
PyMethodDef_size := A_PtrSize + A_PtrSize + 8 + A_PtrSize
VarSetCapacity(AHKMethods, PyMethodDef_size * 2, 0)
offset := 0
NumPut(&AHKMethod_call_cmd_name, AHKMethods, offset), offset += A_PtrSize
NumPut(AHKMethod_call_cmd_meth, AHKMethods, offset), offset += A_PtrSize
NumPut(AHKMethod_call_cmd_flags, AHKMethods, offset, "Int64"), offset += 8
NumPut(&AHKMethod_call_cmd_doc, AHKMethods, offset), offset += A_PtrSize
NumPut(NULL, AHKMethods, offset), offset += A_PtrSize
NumPut(NULL, AHKMethods, offset), offset += A_PtrSize
NumPut(0, AHKMethods, offset, "Int64"), offset += 8
NumPut(NULL, AHKMethods, offset), offset += A_PtrSize

; static PyModuleDef AHKModule = {
;     PyModuleDef_HEAD_INIT, "ahk", 0, -1, AHKMethods,
;     NULL, NULL, NULL, NULL
; };

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

StrPutVar("_ahk", AHKModule_name)
AHKModule_doc := NULL
AHKModule_size := -1
AHKModule_methods := &AHKMethods
AHKModule_slots := NULL
AHKModule_traverse := NULL
AHKModule_clear := NULL
AHKModule_free := NULL
global AHKModule
VarSetCapacity(AHKModule, 104, 0)
offset := 0
NumPut(1, AHKModule, offset, "Int64"), offset := 40 ; PyModuleDef_HEAD_INIT
NumPut(&AHKModule_name, AHKModule, offset), offset += A_PtrSize
NumPut(AHKModule_doc, AHKModule, offset), offset += A_PtrSize
NumPut(AHKModule_size, AHKModule, offset, "Int64"), offset += 8
NumPut(AHKModule_methods, AHKModule, offset), offset += A_PtrSize
NumPut(AHKModule_slots, AHKModule, offset), offset += A_PtrSize
NumPut(AHKModule_traverse, AHKModule, offset), offset += A_PtrSize
NumPut(AHKModule_clear, AHKModule, offset), offset += A_PtrSize
NumPut(AHKModule_free, AHKModule, offset), offset += A_PtrSize

; static PyObject*
PyInit_ahk()
{
    return DllCall(PYTHON_DLL "\PyModule_Create2"
        , "Ptr", &AHKModule
        , "Int", PYTHON_API_VERSION
        , "Cdecl Ptr")
}

py =
(
try:
    import ctypes
    import os
    import sys
    import _ahk

    ctypes.windll.user32.MessageBoxW(0, f"Hello from Python.", "AHK", 1)

    os.environ["HELLO"] = "Привет"
    hello = _ahk.call_cmd("EnvGet", "HELLO")
    assert hello == os.environ["HELLO"]

    temp = _ahk.call_cmd("EnvGet", "TEMP")
    assert isinstance(temp, str), "EnvGet result must be a string"

    rnd = _ahk.call_cmd("Random", "1", "10")
    assert isinstance(rnd, int), "Random result must be an integer"

    result = _ahk.call_cmd("MsgBox")
    assert result == "", "MsgBox result must be an empty string"
    _ahk.call_cmd("MsgBox", "Hello, мир!")
    _ahk.call_cmd("MsgBox", "4", "", "Do you want to continue? (Press YES or NO)")

    _ahk.call_cmd("Send", "#r")

    _ahk.call_cmd("NoSuchCommand", "A")
except:
    import ctypes
    import traceback
    ctypes.windll.user32.MessageBoxW(0, traceback.format_exc(), "AHK", 1)
)

OnExit, LabelOnExit

; ATTACH_PARENT_PROCESS := -1
; DllCall("AttachConsole", UInt, ATTACH_PARENT_PROCESS)
; DllCall("AllocConsole")

; stdout := FileOpen(DllCall("GetStdHandle", "Int", -11, "Ptr"), "h `n")
; stdout.WriteLine("line 1")
; stdout.__Handle

DllCall("LoadLibrary", Str, PYTHON_DLL)
DllCall(PYTHON_DLL "\PyImport_AppendInittab"
    , Ptr, &AHKModule_name ; `AStr, "_ahk"` doesn't work for some reason
    , Ptr, RegisterCallback("PyInit_ahk", "C", 0)
    , Cdecl)
DllCall(PYTHON_DLL "\Py_Initialize", Cdecl)
DllCall(PYTHON_DLL "\PyRun_SimpleString", AStr, py, Cdecl)
; TODO: Show Python syntax errors.
DllCall(PYTHON_DLL "\Py_Finalize", Cdecl)


; END AUTO-EXECUTE SECTION
return


/**
* Wrapper for SKAN's function (see below)
*/
getArgs() {
    CmdLine := DllCall("GetCommandLine", "Str")
    CmdLine := RegExReplace(CmdLine, " /ErrorStdOut", "")
    Skip := (A_IsCompiled ? 1 : 2)
    argv := Args(CmdLine, Skip)
    return argv
}

/**
* By SKAN,  http://goo.gl/JfMNpN,  CD:23/Aug/2014 | MD:24/Aug/2014
*/
Args(CmdLine := "", Skip := 0) {
    pArgs := 0, nArgs := 0, A := []
    pArgs := DllCall( "Shell32\CommandLineToArgvW", WStr, CmdLine, PtrP, nArgs, Ptr)
    Loop % (nArgs)
        if (A_Index > Skip)
            A[A_Index - Skip] := StrGet(NumGet((A_Index - 1) * A_PtrSize + pArgs), "UTF-16")
    return A, A[0] := nArgs - Skip, DllCall("LocalFree", "Ptr", pArgs)
}

trigger(key, args*) {
    ; closure := closures[key]
    ; if (closure) {
    ;     return closure.call(0, args*)
    ; }
}

end(message) {
    message .= "`nThe application will now exit."
    MsgBox % message
    ExitApp
}

GuiClose:
    if (trigger("GuiClose") == 0) {
        return
    }
    ExitApp
    return

GuiContextMenu:
GuiDropFiles:
GuiEscape:
GuiSize:
OnClipboardChange:
    trigger(A_ThisLabel)
    return

LabelOnExit:
    if (trigger("OnExit") == 0) {
        return
    }
    ExitApp
    return

LabelHotkey:
    trigger("Hotkey" . A_ThisHotkey)
    return

OnMessageClosure(wParam, lParam, msg, hwnd){
    trigger("OnMessage" . msg, wParam, lParam, msg, hwnd)
}

#Include %A_ScriptDir%\lib\API.ahk
