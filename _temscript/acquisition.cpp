#include "temscript.h"
#include "defines.h"
#include "types.h"

static PyObject* Acquisition_get_Cameras(Acquisition *self, void *)
{
    TEMScripting::CCDCameras* collection;
    
    HRESULT result = self->iface->get_Cameras(&collection);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    long count;
    result = collection->get_Count(&count);
    if (FAILED(result)) {
        collection->Release();
        raiseComError(result);
        return NULL;
    }
    if (count < 0) {
        collection->Release();
        PyErr_SetString(PyExc_RuntimeError, "Negative collection size.");
        return NULL;
    }

    PyObject* tuple = PyList_New(count);
    for (long n = 0; n < count; n++) {
        TEMScripting::CCDCamera* camera;

        VARIANT nVariant;
        VariantInit(&nVariant);
        nVariant.lVal = n;
        nVariant.vt   = VT_I4;

        result = collection->get_Item(nVariant, &camera);
        if (FAILED(result)) {
            collection->Release();
            Py_XDECREF(tuple);
            raiseComError(result);
            return NULL;
        }

        PyObject* obj = CCDCamera_create(camera);
        if (!obj) {
            camera->Release();
            collection->Release();
            Py_XDECREF(tuple);
            return NULL;
        }

        //PyObject* name = CCDCamera_get_Name(obj);

        PyList_SetItem(tuple, n, obj);
    }

    collection->Release();
    return tuple;
}

static PyObject* Acquisition_get_Detectors(Acquisition *self, void *)
{
    TEMScripting::STEMDetectors* collection;
    
    HRESULT result = self->iface->get_Detectors(&collection);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    long count;
    result = collection->get_Count(&count);
    if (FAILED(result)) {
        collection->Release();
        raiseComError(result);
        return NULL;
    }
    if (count < 0) {
        collection->Release();
        PyErr_SetString(PyExc_RuntimeError, "Negative collection size.");
        return NULL;
    }

    // Get global acquisition parameters
    TEMScripting::STEMAcqParams* params_iface;
    result = collection->get_AcqParams(&params_iface);
    if (FAILED(result)) {
        collection->Release();
        raiseComError(result);
        return NULL;
    }
    PyObject* acqParams = STEMAcqParams_create(params_iface);
    if (!acqParams) {
        params_iface->Release();
        collection->Release();
        return 0;
    }

    PyObject* tuple = PyList_New(count);
    for (long n = 0; n < count; n++) {
        TEMScripting::STEMDetector* detector;

        VARIANT nVariant;
        VariantInit(&nVariant);
        nVariant.lVal = n;
        nVariant.vt   = VT_I4;

        result = collection->get_Item(nVariant, &detector);
        if (FAILED(result)) {
            collection->Release();
            Py_CLEAR(acqParams);
            Py_XDECREF(tuple);
            raiseComError(result);
            return NULL;
        }

        PyObject* obj = STEMDetector_create(detector, acqParams);
        if (!obj) {
            detector->Release();
            collection->Release();
            Py_CLEAR(acqParams);
            Py_XDECREF(tuple);
            return NULL;
        }

        PyList_SetItem(tuple, n, obj);
    }

    Py_CLEAR(acqParams);
    collection->Release();
    return tuple;
}

static PyObject* Acquisition_AddAcqDevice(Acquisition *self, PyObject* args)
{
    if (!args || PySequence_Size(args) != 1) {
        PyErr_SetString(PyExc_ValueError, "1 argument expected.");
        return NULL;
    }
    PyObject* argObj = PySequence_GetItem(args, 0);
    if (!argObj)
        return NULL;
    
    IDispatch* device;
    device = CCDCamera_query(argObj);
    if (!device)
        device = STEMDetector_query(argObj);
    if (!device) {
        Py_XDECREF(argObj);
        PyErr_SetString(PyExc_TypeError, "Acquisition device expected.");
    }

    HRESULT result = self->iface->raw_AddAcqDevice(device);
    Py_XDECREF(argObj); // argObj keeps reference on device
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Acquisition_AddAcqDeviceByName(Acquisition *self, PyObject* args)
{
    if (!args || PySequence_Size(args) != 1) {
        PyErr_SetString(PyExc_ValueError, "1 argument expected.");
        return NULL;
    }
    PyObject* argObj = PySequence_GetItem(args, 0);
    if (!argObj)
        return NULL;
    
    PyObject* nameObj = PyUnicode_FromObject(argObj);
    Py_XDECREF(argObj);
    if (!nameObj)
        return NULL;

    BSTR str = SysAllocStringLen(PyUnicode_AS_UNICODE(nameObj), PyUnicode_GetSize(nameObj));
    Py_XDECREF(nameObj);

    HRESULT result = self->iface->raw_AddAcqDeviceByName(str);
    SysFreeString(str);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Acquisition_RemoveAcqDevice(Acquisition *self, PyObject* args)
{
    if (!args || PySequence_Size(args) != 1) {
        PyErr_SetString(PyExc_ValueError, "1 argument expected.");
        return NULL;
    }
    PyObject* argObj = PySequence_GetItem(args, 0);
    if (!argObj)
        return NULL;
    
    IDispatch* device;
    device = CCDCamera_query(argObj);
    if (!device)
        device = STEMDetector_query(argObj);
    if (!device) {
        Py_XDECREF(argObj);
        PyErr_SetString(PyExc_TypeError, "Acquisition device expected.");
    }

    HRESULT result = self->iface->raw_RemoveAcqDevice(device);
    Py_XDECREF(argObj); // argObj keeps reference on device
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Acquisition_RemoveAcqDeviceByName(Acquisition *self, PyObject* args)
{
    if (!args || PySequence_Size(args) != 1) {
        PyErr_SetString(PyExc_ValueError, "1 argument expected.");
        return NULL;
    }
    PyObject* argObj = PySequence_GetItem(args, 0);
    if (!argObj)
        return NULL;
    
    PyObject* nameObj = PyUnicode_FromObject(argObj);
    Py_XDECREF(argObj);
    if (!nameObj)
        return NULL;

    BSTR str = SysAllocStringLen(PyUnicode_AS_UNICODE(nameObj), PyUnicode_GetSize(nameObj));
    Py_XDECREF(nameObj);
    
    HRESULT result = self->iface->raw_RemoveAcqDeviceByName(str);
    SysFreeString(str);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Acquisition_RemoveAllAcqDevices(Acquisition *self)
{
    HRESULT result = self->iface->raw_RemoveAllAcqDevices();
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Acquisition_AcquireImages(Acquisition *self)
{
    TEMScripting::AcqImages* collection;
    
    HRESULT result = self->iface->raw_AcquireImages(&collection);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    long count;
    result = collection->get_Count(&count);
    if (FAILED(result)) {
        collection->Release();
        raiseComError(result);
        return NULL;
    }
    if (count < 0) {
        collection->Release();
        PyErr_SetString(PyExc_RuntimeError, "Negative collection size.");
        return NULL;
    }

    PyObject* tuple = PyList_New(count);
    for (long n = 0; n < count; n++) {
        TEMScripting::AcqImage* image;

        VARIANT nVariant;
        VariantInit(&nVariant);
        nVariant.lVal = n;
        nVariant.vt   = VT_I4;

        result = collection->get_Item(nVariant, &image);
        if (FAILED(result)) {
            collection->Release();
            Py_XDECREF(tuple);
            raiseComError(result);
            return NULL;
        }

        PyObject* obj = AcqImage_create(image);
        if (!obj) {
            image->Release();
            collection->Release();
            Py_XDECREF(tuple);
            return NULL;
        }
        PyList_SetItem(tuple, n, obj);
    }

    collection->Release();
    return tuple;
}

static PyGetSetDef Acquisition_getset[] = {
    {"Cameras",   (getter)&Acquisition_get_Cameras, NULL, NULL, NULL},
    {"Detectors", (getter)&Acquisition_get_Detectors, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef Acquisition_methods[] = {
    {"AddAcqDevice",            (PyCFunction)&Acquisition_AddAcqDevice, METH_VARARGS, NULL},
    {"AddAcqDeviceByName",      (PyCFunction)&Acquisition_AddAcqDeviceByName, METH_VARARGS, NULL},
    {"RemoveAcqDevice",         (PyCFunction)&Acquisition_RemoveAcqDevice, METH_VARARGS, NULL},
    {"RemoveAcqDeviceByName",   (PyCFunction)&Acquisition_RemoveAcqDeviceByName, METH_VARARGS, NULL},
    {"RemoveAllAcqDevices",     (PyCFunction)&Acquisition_RemoveAllAcqDevices, METH_NOARGS, NULL},
    {"AcquireImages",           (PyCFunction)&Acquisition_AcquireImages, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Acquisition, TEMScripting::Acquisition, Acquisition_getset, Acquisition_methods)
