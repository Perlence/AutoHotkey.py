#NoEnv
#Warn, All, MsgBox

global NULL := 0
; TODO: Find Python DLL with py.exe or in VIRTUAL_ENV.
global PYTHON_DLL := "c:\Users\Sviatoslav\AppData\Local\Programs\Python\Python38\python38.dll"
global METH_VARARGS := 0x0001
global PYTHON_API_VERSION := 1013

global closures := {}

AHKCallCmd(self, args)
{
    ; const char *cmd;
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

    if (!Func("_" cmd)) {
        ; TODO: Raise Python exception.
        end("Unknown command " cmd)
        return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, 1, "Cdecl Ptr")
    }

    if (arg1 == NULL) {
        _%cmd%()
    } else if (arg2 == NULL) {
        _%cmd%(arg1)
    } else if (arg3 == NULL) {
        _%cmd%(arg1, arg2)
    } else if (arg4 == NULL) {
        _%cmd%(arg1, arg2, arg3)
    } else if (arg5 == NULL) {
        _%cmd%(arg1, arg2, arg3, arg4)
    } else if (arg6 == NULL) {
        _%cmd%(arg1, arg2, arg3, arg4, arg5)
    } else if (arg7 == NULL) {
        _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6)
    } else if (arg8 == NULL) {
        _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
    } else if (arg9 == NULL) {
        _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)
    } else if (arg10 == NULL) {
        _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9)
    } else if (arg11 == NULL) {
        _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10)
    } else {
        _%cmd%(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10, arg11)
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

StrPutVar("_ahk", AHKModule_name)
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
    import _ahk
    ctypes.windll.user32.MessageBoxW(0, f"loaded", "AHK", 1)
    _ahk.call_cmd("MsgBox")
    _ahk.call_cmd("MsgBox", "Hello, world")
    _ahk.call_cmd("MsgBox", "4", "", "Do you want to continue? (Press YES or NO)")
    # TODO: Call command with Unicode strings.
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

; stdout := FileOpen(DllCall("GetStdHandle", "int", -11, "ptr"), "h `n")
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
    Local pArgs := 0, nArgs := 0, A := []
    pArgs := DllCall( "Shell32\CommandLineToArgvW", WStr, CmdLine, PtrP, nArgs, Ptr)
    Loop % (nArgs)
        if (A_Index > Skip)
            A[A_Index - Skip] := StrGet(NumGet((A_Index - 1) * A_PtrSize + pArgs), "UTF-16")
    Return A, A[0] := nArgs - Skip, DllCall("LocalFree", "Ptr", pArgs)  
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
