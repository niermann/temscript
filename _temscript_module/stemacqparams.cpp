#include "temscript.h"
#include "defines.h"
#include "types.h"

ENUM_PROPERTY_GETTER(STEMAcqParams, ImageSize, TEMScripting::AcqImageSize)
ENUM_PROPERTY_SETTER(STEMAcqParams, ImageSize, TEMScripting::AcqImageSize)
DOUBLE_PROPERTY_GETTER(STEMAcqParams, DwellTime)
DOUBLE_PROPERTY_SETTER(STEMAcqParams, DwellTime)
LONG_PROPERTY_GETTER(STEMAcqParams, Binning)
LONG_PROPERTY_SETTER(STEMAcqParams, Binning)

static PyGetSetDef STEMAcqParams_getset[] = {
    {"ImageSize",               (getter)&STEMAcqParams_get_ImageSize, (setter)&STEMAcqParams_set_ImageSize, NULL, NULL},
    {"DwellTime",               (getter)&STEMAcqParams_get_DwellTime, (setter)&STEMAcqParams_set_DwellTime, NULL, NULL},
    {"Binning",                 (getter)&STEMAcqParams_get_Binning, (setter)&STEMAcqParams_set_Binning, NULL, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(STEMAcqParams, TEMScripting::STEMAcqParams, STEMAcqParams_getset, 0)

