#include "temscript.h"
#include "defines.h"
#include "types.h"

ENUM_PROPERTY_GETTER(Vacuum, Status, TEMScripting::VacuumStatus)
BOOL_PROPERTY_GETTER(Vacuum, PVPRunning)
BOOL_PROPERTY_GETTER(Vacuum, ColumnValvesOpen)
BOOL_PROPERTY_SETTER(Vacuum, ColumnValvesOpen)

static PyObject* Vacuum_get_Gauges(Vacuum *self, void *)
{
    TEMScripting::Gauges* collection;
    
    HRESULT result = self->iface->get_Gauges(&collection);
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

    PyObject* tuple = PyTuple_New(count);
    for (long n = 0; n < count; n++) {
        TEMScripting::Gauge* gauge;

        VARIANT nVariant;
        VariantInit(&nVariant);
        nVariant.lVal = n;
        nVariant.vt   = VT_I4;

        result = collection->get_Item(nVariant, &gauge);
        if (FAILED(result)) {
            collection->Release();
            Py_XDECREF(tuple);
            raiseComError(result);
            return NULL;
        }

        PyObject* obj = Gauge_create(gauge);
        if (!obj) {
            gauge->Release();
            collection->Release();
            Py_XDECREF(tuple);
            return NULL;
        }
        PyTuple_SetItem(tuple, n, obj);
    }

    collection->Release();
    return tuple;
}

static PyObject* Vacuum_RunBufferCycle(Vacuum *self)
{
    HRESULT result = self->iface->raw_RunBufferCycle();
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyGetSetDef Vacuum_getset[] = {
    {"Status",              (getter)&Vacuum_get_Status, NULL, NULL, NULL},
    {"PVPRunning",          (getter)&Vacuum_get_PVPRunning, NULL, NULL, NULL},
    {"ColumnValvesOpen",    (getter)&Vacuum_get_ColumnValvesOpen, (setter)&Vacuum_set_ColumnValvesOpen, NULL, NULL},
    {"Gauges",              (getter)&Vacuum_get_Gauges, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef Vacuum_methods[] = {
    {"RunBufferCycle",      (PyCFunction)Vacuum_RunBufferCycle, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Vacuum, TEMScripting::Vacuum, Vacuum_getset, Vacuum_methods)
