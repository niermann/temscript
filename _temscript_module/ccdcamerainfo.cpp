#include "temscript.h"
#include "defines.h"
#include "types.h"

STRING_PROPERTY_GETTER(CCDCameraInfo, Name)
LONG_PROPERTY_GETTER(CCDCameraInfo, Width)
LONG_PROPERTY_GETTER(CCDCameraInfo, Height)
VECTOR_PROPERTY_GETTER(CCDCameraInfo, PixelSize)
ARRAY_PROPERTY_GETTER(CCDCameraInfo, Binnings)
ENUM_PROPERTY_GETTER(CCDCameraInfo, ShutterMode, TEMScripting::AcqShutterMode)
ENUM_PROPERTY_SETTER(CCDCameraInfo, ShutterMode, TEMScripting::AcqShutterMode)
ARRAY_PROPERTY_GETTER(CCDCameraInfo, ShutterModes)

static PyGetSetDef CCDCameraInfo_getset[] = {
    {"Name",        (getter)&CCDCameraInfo_get_Name, NULL, NULL, NULL},
    {"Width",       (getter)&CCDCameraInfo_get_Width, NULL, NULL, NULL},
    {"Height",      (getter)&CCDCameraInfo_get_Height, NULL, NULL, NULL},
    {"PixelSize",   (getter)&CCDCameraInfo_get_PixelSize, NULL, NULL, NULL},
    {"Binnings",    (getter)&CCDCameraInfo_get_Binnings, NULL, NULL, NULL},
    {"ShutterModes",(getter)&CCDCameraInfo_get_ShutterModes, NULL, NULL, NULL},
    {"ShutterMode", (getter)&CCDCameraInfo_get_ShutterMode, (setter)&CCDCameraInfo_set_ShutterMode, NULL, NULL},
    {NULL}          /* Sentinel */
};

IMPLEMENT_WRAPPER(CCDCameraInfo, TEMScripting::CCDCameraInfo, CCDCameraInfo_getset, 0)
