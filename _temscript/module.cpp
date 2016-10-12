#include "temscript.h"
#include "types.h"
#include <numpy/arrayobject.h>

#define _WIN32_DCOM //this must be defined (undocumented in MSDN)
#include <objbase.h>

// Helpers
void raiseComError(HRESULT result)
{
    PyObject* args = PyTuple_New(2);
#if PY_MAJOR_VERSION >= 3
    PyTuple_SetItem(args, 0, PyLong_FromLong((long)result));
    PyTuple_SetItem(args, 1, PyUnicode_FromFormat("HRESULT=0x%08x", (int)result));
#else
    PyTuple_SetItem(args, 0, PyInt_FromLong((long)result));
    PyTuple_SetItem(args, 1, PyString_FromFormat("HRESULT=0x%08x", (int)result));
#endif
    PyErr_SetObject(comError, args);
    //PyErr_Format(comError, "HRESULT=0x%08x", (int)result);
}

PyObject* arrayFromSafeArray(SAFEARRAY* arr)
{
    UINT ndim = SafeArrayGetDim(arr);
    if (ndim == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Expected array to be non-scalar");
        return NULL;
    }

    npy_intp* dims = new npy_intp[ndim];
    for (UINT i = 0; i < ndim; i++ ) {
        long lower, upper;
        HRESULT result = SafeArrayGetUBound(arr, 1 + i, &upper);    // Surprise: 1-Indexed
        if (FAILED(result)) {
            delete[] dims;
            raiseComError(result);
            return NULL;
        }   

        result = SafeArrayGetLBound(arr, 1 + i, &lower);    // Surprise: 1-Indexed
        if (FAILED(result)) {
            delete[] dims;
            raiseComError(result);
            return NULL;
        }   

        if (upper <= lower) {
            delete[] dims;
            PyErr_Format(PyExc_RuntimeError, "Expected array bounds of dim %d to be lower < upper: lower=%d, upper=%d.", i, lower, upper);
            return NULL;
        }

        dims[i] = 1 + upper - lower;
    }

    VARTYPE vtype;
    HRESULT result = SafeArrayGetVartype(arr, &vtype);
    if (FAILED(result)) {
        delete[] dims;
        raiseComError(result);
        return NULL;
    }

    int npType;
    switch (vtype) {
    case VT_I1:   npType = NPY_INT8; break;
    case VT_I2:   npType = NPY_INT16; break;
    case VT_I4:   npType = NPY_INT32; break;
    case VT_UI1:  npType = NPY_UINT8; break;
    case VT_UI2:  npType = NPY_UINT16; break;
    case VT_UI4:  npType = NPY_UINT32; break;
    case VT_R4:   npType = NPY_FLOAT32; break;
    case VT_R8:   npType = NPY_FLOAT64; break;
    case VT_INT:  npType = NPY_INT; break;
    case VT_UINT: npType = NPY_UINT; break;
    default:
        delete[] dims;
        PyErr_Format(PyExc_RuntimeError, "Unknown array VARTYPE: %d.", vtype);
        return NULL;
    }

    void *data;
    result = SafeArrayAccessData(arr, &data);
    if (FAILED(result)) {
        delete[] dims;
        raiseComError(result);
        return NULL;
    }

    PyArrayObject* obj = reinterpret_cast<PyArrayObject*>(PyArray_SimpleNew(ndim, dims, npType));
    delete[] dims;
    if (!obj) {
        SafeArrayUnaccessData(arr);
        return NULL;
    }

    memcpy(PyArray_DATA(obj), data, PyArray_NBYTES(obj));
        SafeArrayUnaccessData(arr);

    return reinterpret_cast<PyObject*>(obj);
}

PyObject* tupleFromVector(TEMScripting::Vector* vec)
{
    double x, y;
    
    HRESULT result = vec->get_X(&x);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    result = vec->get_Y(&y);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    PyObject* tuple = PyTuple_New(2);
    if (!tuple)
        return NULL;
    PyTuple_SetItem(tuple, 0, PyFloat_FromDouble(x));
    PyTuple_SetItem(tuple, 1, PyFloat_FromDouble(y));

    return tuple;
}

bool setVectorFromSequence(TEMScripting::Vector* vec, PyObject* seq)
{
    Py_ssize_t len = PySequence_Length(seq);
    if (len < 0)
        return false;
    if (len != 2) {
        PyErr_SetString(PyExc_ValueError, "Expected sequence with two items.");
        return false;
    }

    PyObject* obj = PySequence_GetItem(seq, 0);
    if (!obj) 
        return false;
    PyObject* fltObj = PyNumber_Float(obj);
    Py_DECREF(obj);
    if (!fltObj)
        return false;
    double x = PyFloat_AsDouble(fltObj);
    Py_DECREF(fltObj);

    obj = PySequence_GetItem(seq, 1);
    if (!obj) 
        return false;
    fltObj = PyNumber_Float(obj);
    Py_DECREF(obj);
    if (!fltObj)
        return false;
    double y = PyFloat_AsDouble(fltObj);
    Py_DECREF(fltObj);

    HRESULT result = vec->put_X(x);
    if (FAILED(result)) {
        raiseComError(result);
        return false;
    }

    result = vec->put_Y(y);
    if (FAILED(result)) {
        raiseComError(result);
        return false;
    }

    return true;
}

// Global objects
PyObject* comError = NULL;
PyObject* temscriptModule = NULL;

static PyObject* getInstrument(void)
{
    TEMScripting::InstrumentInterface* iface;
    HRESULT result = CoCreateInstance(TEMScripting::CLSID_Instrument, NULL, CLSCTX_ALL, 
        TEMScripting::IID_InstrumentInterface, (void**)&iface);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    PyObject* obj = Instrument_create(iface);
    if (!obj)
        iface->Release();
    return obj;
}

static PyMethodDef methods[] = {
    {"GetInstrument", (PyCFunction)getInstrument, METH_NOARGS, "Returns Instrument instance."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

#define INIT_ERROR NULL

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT, "_temscript", NULL, -1, methods
};

extern "C" PyMODINIT_FUNC PyInit__temscript(void)

#else

#define INIT_ERROR

extern "C" void init_temscript(void)

#endif

{   
    import_array();
    HRESULT result = CoInitializeEx(NULL, 0);
    if (FAILED(result)) {
        printf("CoInitializeEx failed. HRESULT=%08x\n", result);
        return INIT_ERROR;
    }
    
    // Initialize types
    if (PyType_Ready(&Stage_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&CCDCamera_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&CCDCameraInfo_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&CCDAcqParams_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&STEMDetector_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&STEMDetectorInfo_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&STEMAcqParams_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&AcqImage_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Acquisition_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Gauge_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Vacuum_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Configuration_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Projection_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Illumination_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Gun_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&BlankerShutter_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&InstrumentModeControl_Type) < 0) return INIT_ERROR;
    if (PyType_Ready(&Instrument_Type) < 0) return INIT_ERROR;

    // Initialize module
#if PY_MAJOR_VERSION >= 3
    temscriptModule = PyModule_Create(&moduledef);
#else
    temscriptModule = Py_InitModule("_temscript", methods);
#endif
    if (!temscriptModule)
        return INIT_ERROR;

    // Add exception
    comError = PyErr_NewException("temscript.COMError", NULL, NULL);
    Py_INCREF(comError);
    PyModule_AddObject(temscriptModule, "COMError", comError);

    // Add types
    Py_INCREF(&Stage_Type);
    Py_INCREF(&CCDCamera_Type);
    Py_INCREF(&CCDCameraInfo_Type);
    Py_INCREF(&CCDAcqParams_Type);
    Py_INCREF(&STEMDetector_Type);
    Py_INCREF(&STEMDetectorInfo_Type);
    Py_INCREF(&STEMAcqParams_Type);
    Py_INCREF(&AcqImage_Type);
    Py_INCREF(&Acquisition_Type);
    Py_INCREF(&Gauge_Type);
    Py_INCREF(&Vacuum_Type);
    Py_INCREF(&Configuration_Type);
    Py_INCREF(&Projection_Type);
    Py_INCREF(&Illumination_Type);
    Py_INCREF(&Gun_Type);
    Py_INCREF(&BlankerShutter_Type);
    Py_INCREF(&InstrumentModeControl_Type);
    Py_INCREF(&Instrument_Type);

    PyModule_AddObject(temscriptModule, "Stage", (PyObject *)&Stage_Type);
    PyModule_AddObject(temscriptModule, "CCDCamera", (PyObject *)&CCDCamera_Type);
    PyModule_AddObject(temscriptModule, "CCDCameraInfo", (PyObject *)&CCDCameraInfo_Type);
    PyModule_AddObject(temscriptModule, "CCDAcqParams", (PyObject *)&CCDAcqParams_Type);
    PyModule_AddObject(temscriptModule, "STEMDetector", (PyObject *)&STEMDetector_Type);
    PyModule_AddObject(temscriptModule, "STEMDetectorInfo", (PyObject *)&STEMDetectorInfo_Type);
    PyModule_AddObject(temscriptModule, "STEMAcqParams", (PyObject *)&STEMAcqParams_Type);
    PyModule_AddObject(temscriptModule, "AcqImage", (PyObject *)&AcqImage_Type);
    PyModule_AddObject(temscriptModule, "Acquisition", (PyObject *)&Acquisition_Type);
    PyModule_AddObject(temscriptModule, "Gauge", (PyObject *)&Gauge_Type);
    PyModule_AddObject(temscriptModule, "Vacuum", (PyObject *)&Vacuum_Type);
    PyModule_AddObject(temscriptModule, "Configuration", (PyObject *)&Configuration_Type);
    PyModule_AddObject(temscriptModule, "Projection", (PyObject *)&Projection_Type);
    PyModule_AddObject(temscriptModule, "Illumination", (PyObject *)&Illumination_Type);
    PyModule_AddObject(temscriptModule, "Gun", (PyObject *)&Gun_Type);
    PyModule_AddObject(temscriptModule, "BlankerShutter", (PyObject *)&BlankerShutter_Type);
    PyModule_AddObject(temscriptModule, "InstrumentModeControl", (PyObject *)&InstrumentModeControl_Type);
    PyModule_AddObject(temscriptModule, "Instrument", (PyObject *)&Instrument_Type);

#if PY_MAJOR_VERSION >= 3
    return temscriptModule;
#endif 
}
