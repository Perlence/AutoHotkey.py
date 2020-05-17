#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* Return the number of arguments of the application command line */
static PyObject*
ahk_callcmd(PyObject *self, PyObject *args)
{
    const char *cmd;
    if(!PyArg_ParseTuple(args, "s:callcmd", &cmd))
        return NULL;
    printf("%s", cmd);
    Py_RETURN_NONE;
}

static PyMethodDef AHKMethods[] = {
    {"callcmd", ahk_callcmd, METH_VARARGS,
     "Return the number of arguments received by the process."},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef AHKModule = {
    PyModuleDef_HEAD_INIT, "ahk", NULL, -1, AHKMethods,
    NULL, NULL, NULL, NULL
};

static PyObject*
PyInit_ahk(void)
{
    return PyModule_Create(&AHKModule);
}

int
main(int argc, char *argv[])
{
    // wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    // if (program == NULL) {
    //     fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
    //     exit(1);
    // }
    // Py_SetProgramName(program);  /* optional but recommended */
    PyImport_AppendInittab("ahk", &PyInit_ahk);
    Py_Initialize();
    PyRun_SimpleString(
        "import ahk\n"
        "ahk.callcmd('MsgBox')\n"
    );
    Py_Finalize();
    // if (Py_FinalizeEx() < 0) {
    //     exit(120);
    // }
    // PyMem_RawFree(program);
    return 0;
}
