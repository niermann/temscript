#include "temscript.h"
#include "defines.h"
#include "types.h"

STRING_PROPERTY_GETTER(STEMDetectorInfo, Name)
DOUBLE_PROPERTY_GETTER(STEMDetectorInfo, Brightness)
DOUBLE_PROPERTY_SETTER(STEMDetectorInfo, Brightness)
DOUBLE_PROPERTY_GETTER(STEMDetectorInfo, Contrast)
DOUBLE_PROPERTY_SETTER(STEMDetectorInfo, Contrast)
ARRAY_PROPERTY_GETTER(STEMDetectorInfo, Binnings)

static PyGetSetDef STEMDetectorInfo_getset[] = {
    {"Name",        (getter)&STEMDetectorInfo_get_Name, NULL, NULL, NULL},
    {"Brightness",  (getter)&STEMDetectorInfo_get_Brightness, (setter)&STEMDetectorInfo_set_Brightness, NULL, NULL},
    {"Contrast",    (getter)&STEMDetectorInfo_get_Contrast, (setter)&STEMDetectorInfo_set_Contrast, NULL, NULL},
    {"Binnings",    (getter)&STEMDetectorInfo_get_Binnings, NULL, NULL, NULL},
    {NULL}          /* Sentinel */
};

IMPLEMENT_WRAPPER(STEMDetectorInfo, TEMScripting::STEMDetectorInfo, STEMDetectorInfo_getset, 0)

