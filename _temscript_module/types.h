#ifndef TYPES_INC
#define TYPES_INC

#include "temscript.h"
#include "defines.h"

DECLARE_WRAPPER(Stage, TEMScripting::Stage)
DECLARE_WRAPPER(Gauge, TEMScripting::Gauge)
DECLARE_WRAPPER(Vacuum, TEMScripting::Vacuum)
DECLARE_WRAPPER(AcqImage, TEMScripting::AcqImage)
DECLARE_WRAPPER(CCDCamera, TEMScripting::CCDCamera)
DECLARE_WRAPPER(CCDAcqParams, TEMScripting::CCDAcqParams)
DECLARE_WRAPPER(CCDCameraInfo, TEMScripting::CCDCameraInfo)
DECLARE_WRAPPER(STEMDetectorInfo, TEMScripting::STEMDetectorInfo)
DECLARE_WRAPPER(STEMAcqParams, TEMScripting::STEMAcqParams)
DECLARE_WRAPPER(Acquisition, TEMScripting::Acquisition)
DECLARE_WRAPPER(Configuration, TEMScripting::Configuration)
DECLARE_WRAPPER(Projection, TEMScripting::Projection)
DECLARE_WRAPPER(Illumination, TEMScripting::Illumination)
DECLARE_WRAPPER(Gun, TEMScripting::Gun)
DECLARE_WRAPPER(BlankerShutter, TEMScripting::BlankerShutter)
DECLARE_WRAPPER(InstrumentModeControl, TEMScripting::InstrumentModeControl)
DECLARE_WRAPPER(Instrument, TEMScripting::InstrumentInterface)

// STEMDetector is handled slightly different
extern PyTypeObject STEMDetector_Type;
PyObject* STEMDetector_create(TEMScripting::STEMDetector* detector, PyObject* acqParams);
TEMScripting::STEMDetector* STEMDetector_query(PyObject* self);

#endif // TYPES_INC
