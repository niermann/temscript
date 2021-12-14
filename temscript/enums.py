from enum import IntEnum


# Not defined by FEI, but used in server/client
class DetectorType(IntEnum):
    CAMERA = 1,
    STEM_DETECTOR = 2


class TEMScriptingError(IntEnum):
    E_NOT_OK = -2147155969              # 0x8004ffff
    E_VALUE_CLIP = -2147155970          # 0x8004fffe
    E_OUT_OF_RANGE = -2147155971        # 0x8004fffd
    E_NOT_IMPLEMENTED = -2147155972     # 0x8004fffc
    # The following are also mentioned in the manual
    E_UNEXPECTED = -2147418113          # 0x8000FFFF
    E_NOTIMPL = -2147467263             # 0x80004001
    E_INVALIDARG = -2147024809          # 0x80070057
    E_ABORT = -2147467260               # 0x80004004
    E_FAIL = -2147467259                # 0x80004005
    E_ACCESSDENIED = -2147024891        # 0x80070005


class VacuumStatus(IntEnum):
    UNKNOWN = 1
    OFF = 2
    CAMERA_AIR = 3
    BUSY = 4
    READY = 5
    ELSE = 6


class GaugeStatus(IntEnum):
    UNDEFINED = 0
    UNDERFLOW = 1
    OVERFLOW = 2
    INVALID = 3
    VALID = 4


class GaugePressureLevel(IntEnum):
    UNDEFINED = 0
    LOW = 1
    LOW_MEDIUM = 2
    MEDIUM_HIGH = 3
    HIGH = 4


class StageStatus(IntEnum):
    READY = 0
    DISABLED = 1
    NOT_READY = 2
    GOING = 3
    MOVING = 4
    WOBBLING = 5
    DISABLE = 1         # Misnaming in temscript 1.X


class MeasurementUnitType(IntEnum):
    UNKNOWN = 0
    METERS = 1
    RADIANS = 2


class StageHolderType(IntEnum):
    NONE = 0
    SINGLE_TILT = 1
    DOUBLE_TILT = 2
    INVALID = 4
    POLARA = 5
    DUAL_AXIS = 6


class StageAxes(IntEnum):
    NONE = 0
    X = 1
    Y = 2
    Z = 4
    A = 8
    B = 16
    XY = 3


class IlluminationNormalization(IntEnum):
    SPOTSIZE = 1
    INTENSITY = 2
    CONDENSER = 3
    MINI_CONDENSER = 4
    OBJECTIVE = 5
    ALL = 6


class IlluminationMode(IntEnum):
    NANOPROBE = 0
    MICROPROBE = 1


class DarkFieldMode(IntEnum):
    OFF = 1
    CARTESIAN = 2
    CONICAL = 3


class CondenserMode(IntEnum):
    PARALLEL = 0
    PROBE = 1


class ProjectionNormalization(IntEnum):
    OBJECTIVE = 10
    PROJECTOR = 11
    ALL = 12


class ProjectionMode(IntEnum):
    IMAGING = 1
    DIFFRACTION = 2


class ProjectionSubMode(IntEnum):
    LM = 1
    M = 2
    SA = 3
    MH = 4
    LAD = 5
    D = 6


class LensProg(IntEnum):
    REGULAR = 1
    EFTEM = 2


class ProjectionDetectorShift(IntEnum):
    ON_AXIS = 0
    NEAR_AXIS = 1
    OFF_AXIS = 2


class ProjDetectorShiftMode(IntEnum):
    AUTO_IGNORE = 1
    MANUAL = 2
    ALIGNMENT = 3


class HighTensionState(IntEnum):
    DISABLED = 1
    OFF = 2
    ON = 3


class InstrumentMode(IntEnum):
    TEM = 0
    STEM = 1


class AcqShutterMode(IntEnum):
    PRE_SPECIMEN = 0
    POST_SPECIMEN = 1
    BOTH = 2


class AcqImageSize(IntEnum):
    FULL = 0
    HALF = 1
    QUARTER = 2


class AcqImageCorrection(IntEnum):
    UNPROCESSED = 0
    DEFAULT = 1


class AcqExposureMode(IntEnum):
    NONE = 0
    SIMULTANEOUS = 1
    PRE_EXPOSURE = 2
    PRE_EXPOSURE_PAUSE = 3


class ProductFamily(IntEnum):
    TECNAI = 0
    TITAN = 1


class ScreenPosition(IntEnum):
    UNKNOWN = 1
    UP = 2
    DOWN = 3


class PlateLabelDateFormat(IntEnum):
    NO_DATA = 0
    DDMMYY = 1
    MMDDYY = 2
    YYMMDD = 3
