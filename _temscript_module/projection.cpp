#include "temscript.h"
#include "defines.h"
#include "types.h"

DOUBLE_PROPERTY_GETTER(Projection, Focus)
DOUBLE_PROPERTY_SETTER(Projection, Focus)
ENUM_PROPERTY_GETTER(Projection, Mode, TEMScripting::ProjectionMode)
ENUM_PROPERTY_SETTER(Projection, Mode, TEMScripting::ProjectionMode)
ENUM_PROPERTY_GETTER(Projection, SubMode, TEMScripting::ProjectionSubMode)
STRING_PROPERTY_GETTER(Projection, SubModeString)
ENUM_PROPERTY_GETTER(Projection, LensProgram, TEMScripting::LensProg)
ENUM_PROPERTY_SETTER(Projection, LensProgram, TEMScripting::LensProg)
DOUBLE_PROPERTY_GETTER(Projection, Magnification)
DOUBLE_PROPERTY_GETTER(Projection, ImageRotation)
DOUBLE_PROPERTY_GETTER(Projection, CameraLength)
LONG_PROPERTY_GETTER(Projection, MagnificationIndex)
LONG_PROPERTY_SETTER(Projection, MagnificationIndex)
LONG_PROPERTY_GETTER(Projection, CameraLengthIndex)
LONG_PROPERTY_SETTER(Projection, CameraLengthIndex)
VECTOR_PROPERTY_GETTER(Projection, ImageShift)
VECTOR_PROPERTY_SETTER(Projection, ImageShift)
VECTOR_PROPERTY_GETTER(Projection, ImageBeamShift)
VECTOR_PROPERTY_SETTER(Projection, ImageBeamShift)
VECTOR_PROPERTY_GETTER(Projection, ImageBeamTilt)
VECTOR_PROPERTY_SETTER(Projection, ImageBeamTilt)
VECTOR_PROPERTY_GETTER(Projection, DiffractionShift)
VECTOR_PROPERTY_SETTER(Projection, DiffractionShift)
VECTOR_PROPERTY_GETTER(Projection, DiffractionStigmator)
VECTOR_PROPERTY_SETTER(Projection, DiffractionStigmator)
VECTOR_PROPERTY_GETTER(Projection, ObjectiveStigmator)
VECTOR_PROPERTY_SETTER(Projection, ObjectiveStigmator)
ENUM_PROPERTY_GETTER(Projection, DetectorShift, TEMScripting::ProjectionDetectorShift)
ENUM_PROPERTY_SETTER(Projection, DetectorShift, TEMScripting::ProjectionDetectorShift)
ENUM_PROPERTY_GETTER(Projection, DetectorShiftMode, TEMScripting::ProjDetectorShiftMode)
ENUM_PROPERTY_SETTER(Projection, DetectorShiftMode, TEMScripting::ProjDetectorShiftMode)
DOUBLE_PROPERTY_GETTER(Projection, ObjectiveExcitation)
DOUBLE_PROPERTY_GETTER(Projection, Defocus)
DOUBLE_PROPERTY_SETTER(Projection, Defocus)
LONG_PROPERTY_GETTER(Projection, ProjectionIndex)
LONG_PROPERTY_SETTER(Projection, ProjectionIndex)
LONG_PROPERTY_GETTER(Projection, SubModeMinIndex)
LONG_PROPERTY_GETTER(Projection, SubModeMaxIndex)

static PyObject* Projection_ResetDefocus(Projection *self)
{
    HRESULT result = self->iface->raw_ResetDefocus();
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject* Projection_ChangeProjectionIndex(Projection *self, PyObject* args)
{
    long diff;
    if (!PyArg_ParseTuple(args, "l", &diff))
        return NULL;

    HRESULT result = self->iface->raw_ChangeProjectionIndex(diff);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* Projection_Normalize(Projection *self, PyObject* args)
{
    long norm;
    if (!PyArg_ParseTuple(args, "l", &norm))
        return NULL;

    HRESULT result = self->iface->raw_Normalize((TEMScripting::ProjectionNormalization)norm);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyGetSetDef Projection_getset[] = {
    {"Mode",                (getter)&Projection_get_Mode, (setter)&Projection_set_Mode, NULL, NULL},
    {"SubMode",             (getter)&Projection_get_SubMode, NULL, NULL, NULL},
    {"SubModeString",       (getter)&Projection_get_SubModeString, NULL, NULL, NULL},
    {"LensProgram",         (getter)&Projection_get_LensProgram, (setter)&Projection_set_LensProgram, NULL, NULL},
    {"Magnification",       (getter)&Projection_get_Magnification, NULL, NULL, NULL},
    {"CameraLength",        (getter)&Projection_get_CameraLength, NULL, NULL, NULL},
    {"ImageRotation",       (getter)&Projection_get_ImageRotation, NULL, NULL, NULL},
    {"MagnificationIndex",  (getter)&Projection_get_MagnificationIndex, (setter)&Projection_set_MagnificationIndex, NULL, NULL},
    {"CameraLengthIndex",   (getter)&Projection_get_CameraLengthIndex, (setter)&Projection_set_CameraLengthIndex, NULL, NULL},
    {"ImageShift",          (getter)&Projection_get_ImageShift, (setter)&Projection_set_ImageShift, NULL, NULL},
    {"ImageBeamShift",      (getter)&Projection_get_ImageBeamShift, (setter)&Projection_set_ImageBeamShift, NULL, NULL},
    {"ImageBeamTilt",       (getter)&Projection_get_ImageBeamTilt, (setter)&Projection_set_ImageBeamTilt, NULL, NULL},
    {"DiffractionShift",    (getter)&Projection_get_DiffractionShift, (setter)&Projection_set_DiffractionShift, NULL, NULL},
    {"DiffractionStigmator",(getter)&Projection_get_DiffractionStigmator, (setter)&Projection_set_DiffractionStigmator, NULL, NULL},
    {"ObjectiveStigmator",  (getter)&Projection_get_ObjectiveStigmator, (setter)&Projection_set_ObjectiveStigmator, NULL, NULL},
    {"DetectorShift",       (getter)&Projection_get_DetectorShift, (setter)&Projection_set_DetectorShift, NULL, NULL},
    {"DetectorShiftMode",   (getter)&Projection_get_DetectorShiftMode, (setter)&Projection_set_DetectorShiftMode, NULL, NULL},
    {"Focus",               (getter)&Projection_get_Focus, (setter)&Projection_set_Focus, NULL, NULL},
    {"Defocus",             (getter)&Projection_get_Defocus, (setter)&Projection_set_Defocus, NULL, NULL},
    {"ObjectiveExcitation", (getter)&Projection_get_ObjectiveExcitation, NULL, NULL, NULL},
    {"ProjectionIndex",     (getter)&Projection_get_ProjectionIndex, (setter)&Projection_set_ProjectionIndex, NULL, NULL},
    {"SubModeMinIndex",     (getter)&Projection_get_SubModeMinIndex, NULL, NULL, NULL},
    {"SubModeMaxIndex",     (getter)&Projection_get_SubModeMaxIndex, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef Projection_methods[] = {
    {"ResetDefocus",            (PyCFunction)&Projection_ResetDefocus, METH_NOARGS, NULL},
    {"ChangeProjectionIndex",   (PyCFunction)&Projection_ChangeProjectionIndex, METH_VARARGS, NULL},
    {"Normalize",               (PyCFunction)&Projection_Normalize, METH_VARARGS, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Projection, TEMScripting::Projection, Projection_getset, Projection_methods)

