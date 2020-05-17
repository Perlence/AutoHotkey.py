#NoEnv
#Warn, All, MsgBox
SetFormat, Integer, Hex

global NULL := 0
global PYTHON_DLL := "c:\Users\Sviatoslav\AppData\Local\Programs\Python\Python38\python38.dll"
global METH_VARARGS := 0x0001
global PYTHON_API_VERSION := 1013

ahk_msg_box(self, args)
{
    local param1 := NULL
    local title := NULL
    local text := NULL
    local timeout := NULL

    if (!DllCall(PYTHON_DLL "\PyArg_ParseTuple"
            , Ptr, args
            , AStr, "|ssss:msg_box"
            , Ptr, &param1
            , Ptr, &title
            , Ptr, &text
            , Ptr, &timeout
            , "Cdecl") ) {
        MsgBox, PyArg_ParseTuple failed
        return NULL
    }

    if (param1 == NULL) {
        ; Press OK to continue.
        MsgBox
        ; TODO: Return None.
        return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, 0, "Cdecl Ptr")
    }

    param1 := NumGet(param1) ; Decode number from binary.
    param1 := StrGet(param1, "CP0") ; Read string from address "param1".

    if (title == NULL) {
        ; Short version of MsgBox
        MsgBox, %param1%
        return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, 0, "Cdecl Ptr")
    }

    title := NumGet(title)
    title := StrGet(title, "CP0")

    text := NumGet(text)
    text := StrGet(text, "CP0")

    timeout := NumGet(timeout)
    timeout := StrGet(timeout, "CP0")

    MsgBox, % param1,%title%,%text%,%timeout%
    return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, 0, "Cdecl Ptr")
}

StrPutVar(string, ByRef var)
{
    local encoding := "CP0"
    VarSetCapacity(var, StrPut(string, encoding))
    return StrPut(string, &var, encoding)
}

; static PyMethodDef AHKMethods[] = {
;     {"msg_box", ahk_msg_box, METH_VARARGS,
;      "docstring blablabla"},
;     {NULL, NULL, 0, NULL}
; };

StrPutVar("msg_box", AHKMethod_msg_box_name)
AHKMethod_msg_box_meth := RegisterCallback("ahk_msg_box", "C")
AHKMethod_msg_box_flags := METH_VARARGS
StrPutVar("Return the number of arguments received by the process.", AHKMethod_msg_box_doc)
PyMethodDef_size := A_PtrSize + A_PtrSize + 8 + A_PtrSize
VarSetCapacity(AHKMethods, PyMethodDef_size * 2, 0)
offset := 0
NumPut(&AHKMethod_msg_box_name, AHKMethods, offset), offset += A_PtrSize
NumPut(AHKMethod_msg_box_meth, AHKMethods, offset), offset += A_PtrSize
NumPut(AHKMethod_msg_box_flags, AHKMethods, offset, "Int64"), offset += 8
NumPut(&AHKMethod_msg_box_doc, AHKMethods, offset), offset += A_PtrSize
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
NumPut(1, AHKModule, offset, "Int64"), offset := 40
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
    ahk.msg_box()
    ahk.msg_box("Hello, world")
    ahk.msg_box("4", "", "Do you want to continue? (Press YES or NO)")
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
