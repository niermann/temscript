#include "temscript.h"
#include "defines.h"
#include "types.h"

OBJECT_PROPERTY_GETTER(CCDCamera, Info, CCDCameraInfo, TEMScripting::CCDCameraInfo)
OBJECT_PROPERTY_GETTER(CCDCamera, AcqParams, CCDAcqParams, TEMScripting::CCDAcqParams)
OBJECT_PROPERTY_SETTER(CCDCamera, AcqParams, CCDAcqParams, TEMScripting::CCDAcqParams)

static PyGetSetDef CCDCamera_getset[] = {
    {"Info",        (getter)&CCDCamera_get_Info, NULL, NULL, NULL},
    {"AcqParams",   (getter)&CCDCamera_get_AcqParams, (setter)&CCDCamera_set_AcqParams, NULL, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(CCDCamera, TEMScripting::CCDCamera, CCDCamera_getset, 0)
