#include "temscript.h"
#include "defines.h"
#include "types.h"

BOOL_PROPERTY_GETTER(InstrumentModeControl, StemAvailable)
ENUM_PROPERTY_GETTER(InstrumentModeControl, InstrumentMode, TEMScripting::InstrumentMode)
ENUM_PROPERTY_SETTER(InstrumentModeControl, InstrumentMode, TEMScripting::InstrumentMode)

static PyGetSetDef InstrumentModeControl_getset[] = {
    {"StemAvailable",   (getter)&InstrumentModeControl_get_StemAvailable, NULL, NULL, NULL},
    {"InstrumentMode",  (getter)&InstrumentModeControl_get_InstrumentMode, (setter)&InstrumentModeControl_set_InstrumentMode, NULL, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(InstrumentModeControl, TEMScripting::InstrumentModeControl, InstrumentModeControl_getset, 0)
