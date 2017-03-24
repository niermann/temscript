#include "temscript.h"
#include "defines.h"
#include "types.h"

ENUM_PROPERTY_GETTER(CCDAcqParams, ImageSize, TEMScripting::AcqImageSize)
ENUM_PROPERTY_SETTER(CCDAcqParams, ImageSize, TEMScripting::AcqImageSize)
DOUBLE_PROPERTY_GETTER(CCDAcqParams, ExposureTime)
DOUBLE_PROPERTY_SETTER(CCDAcqParams, ExposureTime)
LONG_PROPERTY_GETTER(CCDAcqParams, Binning)
LONG_PROPERTY_SETTER(CCDAcqParams, Binning)
ENUM_PROPERTY_GETTER(CCDAcqParams, ImageCorrection, TEMScripting::AcqImageCorrection)
ENUM_PROPERTY_SETTER(CCDAcqParams, ImageCorrection, TEMScripting::AcqImageCorrection)
ENUM_PROPERTY_GETTER(CCDAcqParams, ExposureMode, TEMScripting::AcqExposureMode)
ENUM_PROPERTY_SETTER(CCDAcqParams, ExposureMode, TEMScripting::AcqExposureMode)
DOUBLE_PROPERTY_GETTER(CCDAcqParams, MinPreExposureTime)
DOUBLE_PROPERTY_GETTER(CCDAcqParams, MaxPreExposureTime)
DOUBLE_PROPERTY_GETTER(CCDAcqParams, PreExposureTime)
DOUBLE_PROPERTY_SETTER(CCDAcqParams, PreExposureTime)
DOUBLE_PROPERTY_GETTER(CCDAcqParams, MinPreExposurePauseTime)
DOUBLE_PROPERTY_GETTER(CCDAcqParams, MaxPreExposurePauseTime)
DOUBLE_PROPERTY_GETTER(CCDAcqParams, PreExposurePauseTime)
DOUBLE_PROPERTY_SETTER(CCDAcqParams, PreExposurePauseTime)

static PyGetSetDef CCDAcqParams_getset[] = {
    {"ImageSize",               (getter)&CCDAcqParams_get_ImageSize, (setter)&CCDAcqParams_set_ImageSize, NULL, NULL},
    {"ExposureTime",            (getter)&CCDAcqParams_get_ExposureTime, (setter)&CCDAcqParams_set_ExposureTime, NULL, NULL},
    {"Binning",                 (getter)&CCDAcqParams_get_Binning, (setter)&CCDAcqParams_set_Binning, NULL, NULL},
    {"ImageCorrection",         (getter)&CCDAcqParams_get_ImageCorrection, (setter)&CCDAcqParams_set_ImageCorrection, NULL, NULL},
    {"ExposureMode",            (getter)&CCDAcqParams_get_ExposureMode, (setter)&CCDAcqParams_set_ExposureMode, NULL, NULL},
    {"MinPreExposureTime",      (getter)&CCDAcqParams_get_MinPreExposureTime, NULL, NULL, NULL},
    {"MaxPreExposureTime",      (getter)&CCDAcqParams_get_MaxPreExposureTime, NULL, NULL, NULL},
    {"PreExposureTime",         (getter)&CCDAcqParams_get_PreExposureTime, (setter)&CCDAcqParams_set_PreExposureTime, NULL, NULL},
    {"MinPreExposurePauseTime", (getter)&CCDAcqParams_get_MinPreExposurePauseTime, NULL, NULL, NULL},
    {"MaxPreExposurePauseTime", (getter)&CCDAcqParams_get_MaxPreExposurePauseTime, NULL, NULL, NULL},
    {"PreExposurePauseTime",    (getter)&CCDAcqParams_get_PreExposurePauseTime, (setter)&CCDAcqParams_set_PreExposurePauseTime, NULL, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(CCDAcqParams, TEMScripting::CCDAcqParams, CCDAcqParams_getset, 0)

