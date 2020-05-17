#NoEnv
#Warn, All, MsgBox

global NULL := 0
global PYTHON_DLL := "c:\Users\Sviatoslav\AppData\Local\Programs\Python\Python38\python38.dll"
global METH_VARARGS := 0x0001
global PYTHON_API_VERSION := 1013

AHKCallCmd(self, args)
{
    local cmd := NULL
    ; Maximum number of AHK command arguments seems to be 11
    local arg1 := NULL
    local arg2 := NULL
    local arg3 := NULL
    local arg4 := NULL
    local arg5 := NULL
    local arg6 := NULL
    local arg7 := NULL
    local arg8 := NULL
    local arg9 := NULL
    local arg10 := NULL
    local arg11 := NULL

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
            , "Cdecl") ) {
        return NULL
    }

    cmd := NumGet(cmd) ; Decode number from binary.
    cmd := StrGet(cmd, "CP0") ; Read string from address `cmd`.

    Loop, 11
    {
        if (arg%A_Index% != NULL) {
            arg%A_Index% := NumGet(arg%A_Index%)
            arg%A_Index% := StrGet(arg%A_Index%, "CP0")
        }
    }

    if (cmd == "MsgBox") {
        if (arg1 == NULL) {
            MsgBox
        } else if (arg2 == NULL) {
            MsgBox, %arg1%
        } else {
            MsgBox, % arg1,%arg2%,%arg3%,%arg4%
        }
    } else if (cmd == "Send") {
        Send, %arg1%
    } else {
        ; TODO: Raise Python exception.
        MsgBox, % "Unknown command " cmd
        return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, 1, "Cdecl Ptr")
    }
    ; TODO: Export other AHK commands.
    return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, 0, "Cdecl Ptr")
}

StrPutVar(string, ByRef var)
{
    local encoding := "CP0"
    VarSetCapacity(var, StrPut(string, encoding))
    return StrPut(string, &var, encoding)
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

StrPutVar("ahk", AHKModule_name)
AHKModule_doc := NULL
AHKModule_size := -1
AHKModule_methods := &AHKMethods
AHKModule_slots := NULL
AHKModule_traverse := NULL
AHKModule_clear := NULL
AHKModule_free := NULL
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
    global AHKModule
    return DllCall(PYTHON_DLL "\PyModule_Create2"
        , "Ptr", &AHKModule
        , "Int", PYTHON_API_VERSION
        , "Cdecl Ptr")
}

py =
(
try:
    import ctypes
    import sys
    import ahk
    ctypes.windll.user32.MessageBoxW(0, f"loaded", "AHK", 1)
    ahk.call_cmd("MsgBox")
    ahk.call_cmd("MsgBox", "Hello, world")
    ahk.call_cmd("MsgBox", "4", "", "Do you want to continue? (Press YES or NO)")
    ahk.call_cmd("Send", "#r")
    ahk.call_cmd("WinExist", "A")
except:
    import ctypes
    import traceback
    ctypes.windll.user32.MessageBoxW(0, traceback.format_exc(), "AHK", 1)
)

; ATTACH_PARENT_PROCESS := -1
; DllCall("AllocConsole", Int, ATTACH_PARENT_PROCESS)

; stdout := FileOpen("*", "w")
; stdout.WriteLine("line 2")
; stdout.WriteLine("line 3")
; stdout.__Handle ; flush

DllCall("LoadLibrary", Str, PYTHON_DLL)
DllCall(PYTHON_DLL "\PyImport_AppendInittab"
    , Ptr, &AHKModule_name
    , Ptr, RegisterCallback("PyInit_ahk", "C", 0)
    , Cdecl)
DllCall(PYTHON_DLL "\Py_Initialize", Cdecl)
DllCall(PYTHON_DLL "\PyRun_SimpleString", AStr, py, Cdecl)
; DllCall(PYTHON_DLL "\PyErr_PrintEx", Int, 1)
DllCall(PYTHON_DLL "\Py_Finalize", Cdecl)
