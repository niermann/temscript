#include "temscript.h"
#include "defines.h"
#include "types.h"

BOOL_PROPERTY_GETTER(BlankerShutter, ShutterOverrideOn)
BOOL_PROPERTY_SETTER(BlankerShutter, ShutterOverrideOn)

static PyGetSetDef BlankerShutter_getset[] = {
    {"ShutterOverrideOn",   (getter)&BlankerShutter_get_ShutterOverrideOn, (setter)&BlankerShutter_set_ShutterOverrideOn, NULL, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(BlankerShutter, TEMScripting::BlankerShutter, BlankerShutter_getset, 0)
