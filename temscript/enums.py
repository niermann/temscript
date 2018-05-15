# Get imports from library
try:
    # Python 3.X
    from enum import IntEnum
except ImportError:
    # Python 2.X
    from enum34 import IntEnum

from . import constants as const

__all__ = ("DetectorType", "VacuumStatus", "GaugeStatus", "GaugePressureLevel", "StageStatus", "StageHolderType",
           "IlluminationNormalization", "IlluminationMode", "DarkFieldMode", "CondenserMode", "ProjectionNormalization",
           "ProjectionMode", "ProjectionSubMode", "LensProg", "ProjectionDetectorShift", "ProjDetectorShiftMode",
           "HighTensionState", "InstrumentMode", "AcqShutterMode", "AcqImageSize", "AcqImageCorrection",
           "AcqExposureMode", "ProductFamily")


# Not defined by FEI, but used in server/client
class DetectorType(IntEnum):
    CAMERA = 1,
    STEM_DETECTOR = 2


class VacuumStatus(IntEnum):
    UNKNOWN = const.vsUnknown
    OFF = const.vsOff
    CAMERA_AIR = const.vsCameraAir
    BUSY = const.vsBusy
    READY = const.vsReady
    ELSE = const.vsElse


class GaugeStatus(IntEnum):
    UNDEFINED = const.gsUndefined
    UNDERFLOW = const.gsUnderflow
    OVERFLOW = const.gsOverflow
    INVALID = const.gsInvalid
    VALID = const.gsValid


class GaugePressureLevel(IntEnum):
    UNDEFINED = const.plGaugePressurelevelUndefined
    LOW = const.plGaugePressurelevelLow
    LOW_MEDIUM = const.plGaugePressurelevelLowMedium
    MEDIUM_HIGH = const.plGaugePressurelevelMediumHigh
    HIGH = const.plGaugePressurelevelHigh


class StageStatus(IntEnum):
    READY = const.stReady
    DISABLE = const.stDisabled
    NOT_READY = const.stNotReady
    GOING = const.stGoing
    MOVING = const.stMoving
    WOBBLING = const.stWobbling


class StageHolderType(IntEnum):
    NONE = const.hoNone
    SINGLE_TILT = const.hoSingleTilt
    DOUBLE_TILT = const.hoDoubleTilt
    INVALID = const.hoInvalid
    POLARA = const.hoPolara
    DUAL_AXIS = const.hoDualAxis


class IlluminationNormalization(IntEnum):
    SPOTSIZE = const.nmSpotsize
    INTENSITY = const.nmIntensity
    CONDENSER = const.nmCondenser
    MINI_CONDENSER = const.nmMiniCondenser
    OBJECTIVE = const.nmObjectivePole
    ALL = const.nmAll


class IlluminationMode(IntEnum):
    NANOPROBE = const.imNanoProbe
    MICROPROBE = const.imMicroProbe


class DarkFieldMode(IntEnum):
    OFF = const.dfOff
    CARTESIAN = const.dfCartesian
    CONICAL = const.dfConical


class CondenserMode(IntEnum):
    PARALLEL = const.cmParallelIllumination
    PROBE = const.cmProbeIllumination


class ProjectionNormalization(IntEnum):
    OBJECTIVE = const.pnmObjective
    PROJECTOR = const.pnmProjector
    ALL = const.pnmAll


class ProjectionMode(IntEnum):
    IMAGING = const.pmImaging
    DIFFRACTION = const.pmDiffraction


class ProjectionSubMode(IntEnum):
    LM = const.psmLM
    M = const.psmMi
    SA = const.psmSA
    MH = const.psmMh
    LAD = const.psmLAD
    D = const.psmD


class LensProg(IntEnum):
    REGULAR = const.lpRegular
    EFTEM = const.lpEFTEM


class ProjectionDetectorShift(IntEnum):
    ON_AXIS = const.pdsOnAxis
    NEAR_AXIS = const.pdsNearAxis
    OFF_AXIS = const.pdsOffAxis


class ProjDetectorShiftMode(IntEnum):
    AUTO_IGNORE = const.pdsmAutoIgnore
    MANUAL = const.pdsmManual
    ALIGNMENT = const.pdsmAlignment


class HighTensionState(IntEnum):
    DISABLED = const.htDisabled
    OFF = const.htOff
    ON = const.htOn


class InstrumentMode(IntEnum):
    TEM = const.InstrumentMode_TEM
    STEM = const.InstrumentMode_STEM


class AcqShutterMode(IntEnum):
    PRE_SPECIMEN = const.AcqShutterMode_PreSpecimen
    POST_SPECIMEN = const.AcqShutterMode_PostSpecimen
    BOTH = const.AcqShutterMode_Both


class AcqImageSize(IntEnum):
    FULL = const.AcqImageSize_Full
    HALF = const.AcqImageSize_Half
    QUARTER = const.AcqImageSize_Quarter


class AcqImageCorrection(IntEnum):
    UNPROCESSED = const.AcqImageCorrection_Unprocessed
    DEFAULT = const.AcqImageCorrection_Default


class AcqExposureMode(IntEnum):
    NONE = const.AcqExposureMode_None
    SIMULTANEOUS = const.AcqExposureMode_Simultaneous
    PRE_EXPOSURE = const.AcqExposureMode_PreExposure
    PRE_EXPOSURE_PAUSE = const.AcqExposureMode_PreExposurePause


class ProductFamily(IntEnum):
    TECNAI = const.ProductFamily_Tecnai
    TITAN = const.ProductFamily_Titan
