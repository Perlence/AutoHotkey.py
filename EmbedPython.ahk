#NoEnv
#Warn, All, MsgBox
SetFormat, Integer, Hex

global numargs := 5

global NULL := 0
global PYTHON_DLL := "c:\Users\Sviatoslav\AppData\Local\Programs\Python\Python38\python38.dll"
global METH_VARARGS := 0x0001
global PYTHON_API_VERSION := 1013

; Return the number of arguments of the application command line
; static PyObject*
; ahk_numargs(PyObject *self, PyObject *args)
ahk_numargs(self, args)
{
    if (!DllCall(PYTHON_DLL "\PyArg_ParseTuple", Ptr, args, AStr, ":numargs", "Cdecl")) {
        return 0
    }
    return DllCall(PYTHON_DLL "\PyLong_FromLong", Int, numargs, "Cdecl Ptr")
}

; static PyMethodDef AHKMethods[] = {
;     {"numargs", ahk_numargs, METH_VARARGS,
;      "Return the number of arguments received by the process."},
;     {NULL, NULL, 0, NULL}
; };
PyMethodDef_size := A_PtrSize + A_PtrSize + 8 + A_PtrSize

; PyMethodDef(name, meth, flags, doc) {

; }

; AHKMethod := [
;     PyMethodDef("numargs", RegisterCallback("ahk_numargs", "C", 2), METH_VARARGS, "Return the number of arguments received by the process."),
;     PyMethodDef(NULL, NULL, 0, NULL),
; ]

VarSetCapacity(AHKMethod_numargs_name, 8, 0)
StrPut("numargs", &AHKMethod_numargs_name, "CP1252")
AHKMethod_numargs_meth := RegisterCallback("ahk_numargs", "C")
AHKMethod_numargs_flags := METH_VARARGS
VarSetCapacity(AHKMethod_numargs_doc, 56, 0)
StrPut("Return the number of arguments received by the process.", &AHKMethod_numargs_doc, "CP1252")
VarSetCapacity(AHKMethods, PyMethodDef_size * 2, 0)
offset := 0
NumPut(&AHKMethod_numargs_name, AHKMethods, offset), offset += A_PtrSize
NumPut(AHKMethod_numargs_meth, AHKMethods, offset), offset += A_PtrSize
NumPut(AHKMethod_numargs_flags, AHKMethods, offset, "Int64"), offset += 8
NumPut(&AHKMethod_numargs_doc, AHKMethods, offset), offset += A_PtrSize
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

VarSetCapacity(AHKModule_name, 4, 0)
StrPut("ahk", &AHKModule_name, "CP1252")
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
    ctypes.windll.user32.MessageBoxW(0, f"ahk {ahk}", "AHK", 1)
    ctypes.windll.user32.MessageBoxW(0, f"Number of arguments {ahk.numargs()}", "AHK", 1)
    # print("Number of arguments", ahk.numargs())
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

MsgBox, done
