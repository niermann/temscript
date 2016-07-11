#include "temscript.h"
#include "defines.h"
#include "types.h"

OBJECT_PROPERTY_GETTER(Instrument, Configuration, Configuration, TEMScripting::Configuration)
OBJECT_PROPERTY_GETTER(Instrument, Projection, Projection, TEMScripting::Projection)
OBJECT_PROPERTY_GETTER(Instrument, Illumination, Illumination, TEMScripting::Illumination)
OBJECT_PROPERTY_GETTER(Instrument, Stage, Stage, TEMScripting::Stage)
OBJECT_PROPERTY_GETTER(Instrument, Acquisition, Acquisition, TEMScripting::Acquisition)
OBJECT_PROPERTY_GETTER(Instrument, Vacuum, Vacuum, TEMScripting::Vacuum)
OBJECT_PROPERTY_GETTER(Instrument, Gun, Gun, TEMScripting::Gun)
OBJECT_PROPERTY_GETTER(Instrument, BlankerShutter, BlankerShutter, TEMScripting::BlankerShutter)
OBJECT_PROPERTY_GETTER(Instrument, InstrumentModeControl, InstrumentModeControl, TEMScripting::InstrumentModeControl)
BOOL_PROPERTY_GETTER(Instrument, AutoNormalizeEnabled)
BOOL_PROPERTY_SETTER(Instrument, AutoNormalizeEnabled)

static PyObject* Instrument_NormalizeAll(Instrument *self)
{
    HRESULT result = self->iface->raw_NormalizeAll();
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyGetSetDef Instrument_getset[] = {
    {"Configuration",        (getter)&Instrument_get_Configuration, NULL, NULL, NULL},
    {"Projection",           (getter)&Instrument_get_Projection, NULL, NULL, NULL},
    {"Stage",                (getter)&Instrument_get_Stage, NULL, NULL, NULL},
    {"Acquisition",          (getter)&Instrument_get_Acquisition, NULL, NULL, NULL},
    {"Illumination",         (getter)&Instrument_get_Illumination, NULL, NULL, NULL},
    {"AutoNormalizeEnabled", (getter)&Instrument_get_AutoNormalizeEnabled, (setter)&Instrument_set_AutoNormalizeEnabled, NULL, NULL},
    {"Vacuum",               (getter)&Instrument_get_Vacuum, NULL, NULL, NULL},
    {"Gun",                  (getter)&Instrument_get_Gun, NULL, NULL, NULL},
    {"BlankerShutter",       (getter)&Instrument_get_BlankerShutter, NULL, NULL, NULL},
    {"InstrumentModeControl",(getter)&Instrument_get_InstrumentModeControl, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef Instrument_methods[] = {
    {"NormalizeAll",    (PyCFunction)&Instrument_NormalizeAll, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Instrument, TEMScripting::InstrumentInterface, Instrument_getset, Instrument_methods)

