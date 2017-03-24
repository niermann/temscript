#include "temscript.h"
#include "defines.h"
#include "types.h"

ENUM_PROPERTY_GETTER(Illumination, Mode, TEMScripting::IlluminationMode)
ENUM_PROPERTY_SETTER(Illumination, Mode, TEMScripting::IlluminationMode)
LONG_PROPERTY_GETTER(Illumination, SpotsizeIndex)
LONG_PROPERTY_SETTER(Illumination, SpotsizeIndex)
DOUBLE_PROPERTY_GETTER(Illumination, Intensity)
DOUBLE_PROPERTY_SETTER(Illumination, Intensity)
BOOL_PROPERTY_GETTER(Illumination, IntensityZoomEnabled)
BOOL_PROPERTY_SETTER(Illumination, IntensityZoomEnabled)
BOOL_PROPERTY_GETTER(Illumination, IntensityLimitEnabled)
BOOL_PROPERTY_SETTER(Illumination, IntensityLimitEnabled)
BOOL_PROPERTY_GETTER(Illumination, BeamBlanked)
BOOL_PROPERTY_SETTER(Illumination, BeamBlanked)
VECTOR_PROPERTY_GETTER(Illumination, Shift)
VECTOR_PROPERTY_SETTER(Illumination, Shift)
VECTOR_PROPERTY_GETTER(Illumination, Tilt)
VECTOR_PROPERTY_SETTER(Illumination, Tilt)
VECTOR_PROPERTY_GETTER(Illumination, RotationCenter)
VECTOR_PROPERTY_SETTER(Illumination, RotationCenter)
VECTOR_PROPERTY_GETTER(Illumination, CondenserStigmator)
VECTOR_PROPERTY_SETTER(Illumination, CondenserStigmator)
ENUM_PROPERTY_GETTER(Illumination, DFMode, TEMScripting::DarkFieldMode)
ENUM_PROPERTY_SETTER(Illumination, DFMode, TEMScripting::DarkFieldMode)
ENUM_PROPERTY_GETTER(Illumination, CondenserMode, TEMScripting::CondenserMode)
ENUM_PROPERTY_SETTER(Illumination, CondenserMode, TEMScripting::CondenserMode)
DOUBLE_PROPERTY_GETTER(Illumination, IlluminatedArea)
DOUBLE_PROPERTY_GETTER(Illumination, ProbeDefocus)
DOUBLE_PROPERTY_GETTER(Illumination, StemMagnification)
DOUBLE_PROPERTY_SETTER(Illumination, StemMagnification)
DOUBLE_PROPERTY_GETTER(Illumination, StemRotation)
DOUBLE_PROPERTY_SETTER(Illumination, StemRotation)

static PyObject* Illumination_Normalize(Illumination *self, PyObject* args)
{
    long norm;
    if (!PyArg_ParseTuple(args, "l", &norm))
        return NULL;

    HRESULT result = self->iface->raw_Normalize((TEMScripting::IlluminationNormalization)norm);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyGetSetDef Illumination_getset[] = {
    {"Mode",                (getter)&Illumination_get_Mode, (setter)&Illumination_set_Mode, NULL, NULL},
    {"SpotSizeIndex",       (getter)&Illumination_get_SpotsizeIndex, (setter)&Illumination_set_SpotsizeIndex, NULL, NULL},
    {"Intensity",           (getter)&Illumination_get_Intensity, (setter)&Illumination_set_Intensity, NULL, NULL},
    {"IntensityZoomEnabled",(getter)&Illumination_get_IntensityZoomEnabled, (setter)&Illumination_set_IntensityZoomEnabled, NULL, NULL},
    {"IntensityLimitEnabled",(getter)&Illumination_get_IntensityLimitEnabled, (setter)&Illumination_set_IntensityLimitEnabled, NULL, NULL},
    {"BeamBlanked",         (getter)&Illumination_get_BeamBlanked, (setter)&Illumination_set_BeamBlanked, NULL, NULL},
    {"Shift",               (getter)&Illumination_get_Shift, (setter)&Illumination_set_Shift, NULL, NULL},
    {"Tilt",                (getter)&Illumination_get_Tilt, (setter)&Illumination_set_Tilt, NULL, NULL},
    {"RotationCenter",      (getter)&Illumination_get_RotationCenter, (setter)&Illumination_set_RotationCenter, NULL, NULL},
    {"CondenserStigmator",  (getter)&Illumination_get_CondenserStigmator, (setter)&Illumination_set_CondenserStigmator, NULL, NULL},
    {"DFMode",              (getter)&Illumination_get_DFMode, (setter)&Illumination_set_DFMode, NULL, NULL},
    {"DarkFieldMode",       (getter)&Illumination_get_DFMode, (setter)&Illumination_set_DFMode, NULL, NULL},
    {"CondenserMode",       (getter)&Illumination_get_CondenserMode, (setter)&Illumination_set_CondenserMode, NULL, NULL},
    {"IlluminatedArea",     (getter)&Illumination_get_IlluminatedArea, NULL, NULL, NULL},
    {"ProbeDefocus",        (getter)&Illumination_get_ProbeDefocus, NULL, NULL, NULL},
    {"StemMagnification",   (getter)&Illumination_get_StemMagnification, (setter)&Illumination_set_StemMagnification, NULL, NULL},
    {"StemRotation",        (getter)&Illumination_get_StemRotation, (setter)&Illumination_set_StemRotation, NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef Illumination_methods[] = {
    {"Normalize",               (PyCFunction)&Illumination_Normalize, METH_VARARGS, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Illumination, TEMScripting::Illumination, Illumination_getset, Illumination_methods)
