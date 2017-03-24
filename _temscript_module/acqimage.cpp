#include "temscript.h"
#include "defines.h"
#include "types.h"

STRING_PROPERTY_GETTER(AcqImage, Name)
LONG_PROPERTY_GETTER(AcqImage, Width)
LONG_PROPERTY_GETTER(AcqImage, Height)
LONG_PROPERTY_GETTER(AcqImage, Depth)
ARRAY_PROPERTY_GETTER(AcqImage, AsSafeArray)

static PyGetSetDef AcqImage_getset[] = {
    {"Name",    (getter)&AcqImage_get_Name, NULL, NULL, NULL},
    {"Width",   (getter)&AcqImage_get_Width, NULL, NULL, NULL},
    {"Height",  (getter)&AcqImage_get_Height, NULL, NULL, NULL},
    {"Depth",   (getter)&AcqImage_get_Depth, NULL, NULL, NULL},
    {"Array",   (getter)&AcqImage_get_AsSafeArray, NULL, NULL, NULL},   // Renamed property
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(AcqImage, TEMScripting::AcqImage, AcqImage_getset, 0)
