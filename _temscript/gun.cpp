#include "temscript.h"
#include "defines.h"
#include "types.h"

ENUM_PROPERTY_GETTER(Gun, HTState, TEMScripting::HightensionState)
ENUM_PROPERTY_SETTER(Gun, HTState, TEMScripting::HightensionState)
DOUBLE_PROPERTY_GETTER(Gun, HTValue)
DOUBLE_PROPERTY_SETTER(Gun, HTValue)
DOUBLE_PROPERTY_GETTER(Gun, HTMaxValue)
VECTOR_PROPERTY_GETTER(Gun, Shift)
VECTOR_PROPERTY_SETTER(Gun, Shift)
VECTOR_PROPERTY_GETTER(Gun, Tilt)
VECTOR_PROPERTY_SETTER(Gun, Tilt)

static PyGetSetDef Gun_getset[] = {
    {"HTState",         (getter)&Gun_get_HTState, (setter)&Gun_set_HTState, NULL, NULL},
    {"HTValue",         (getter)&Gun_get_HTValue, (setter)&Gun_set_HTValue, NULL, NULL},
    {"HTMaxValue",      (getter)&Gun_get_HTMaxValue, NULL, NULL, NULL},
    {"Shift",           (getter)&Gun_get_Shift, (setter)&Gun_set_Shift, NULL, NULL},
    {"Tilt",            (getter)&Gun_get_Tilt, (setter)&Gun_set_Tilt, NULL, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Gun, TEMScripting::Gun, Gun_getset, 0)
