#include "temscript.h"
#include "defines.h"
#include "types.h"

STRING_PROPERTY_GETTER(Gauge, Name)
DOUBLE_PROPERTY_GETTER(Gauge, Pressure)
ENUM_PROPERTY_GETTER(Gauge, PressureLevel, TEMScripting::GaugePressureLevel)
ENUM_PROPERTY_GETTER(Gauge, Status, TEMScripting::GaugeStatus)

static PyObject* Gauge_Read(Gauge *self)
{
    HRESULT result = self->iface->raw_Read();
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyGetSetDef Gauge_getset[] = {
    {"Name",            (getter)&Gauge_get_Name, NULL, NULL, NULL},
    {"Pressure",        (getter)&Gauge_get_Pressure, NULL, NULL, NULL},
    {"PressureLevel",   (getter)&Gauge_get_PressureLevel, NULL, NULL, NULL},
    {"Status",          (getter)&Gauge_get_Status, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef Gauge_methods[] = {
    {"Read",    (PyCFunction)&Gauge_Read, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Gauge, TEMScripting::Gauge, Gauge_getset, Gauge_methods)
