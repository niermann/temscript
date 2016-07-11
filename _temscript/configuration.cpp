#include "temscript.h"
#include "defines.h"
#include "types.h"

ENUM_PROPERTY_GETTER(Configuration, ProductFamily, TEMScripting::ProductFamily)

static PyGetSetDef Configuration_getset[] = {
    {"ProductFamily",   (getter)&Configuration_get_ProductFamily, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Configuration, TEMScripting::Configuration, Configuration_getset, 0)
