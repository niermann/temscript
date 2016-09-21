# TEMScriptingError
E_NOT_OK = -2147155969
E_VALUE_CLIP = -2147155970
E_OUT_OF_RANGE = -2147155971
E_NOT_IMPLEMENTED = -2147155972

# VacuumStatus
vsUnknown = 1
vsOff = 2
vsCameraAir = 3
vsBusy = 4
vsReady = 5
vsElse = 6

# GaugeStatus
gsUndefined = 0
gsUnderflow = 1
gsOverflow = 2
gsInvalid = 3
gsValid = 4

# GaugePressureLevel
plGaugePressurelevelUndefined = 0
plGaugePressurelevelLow = 1
plGaugePressurelevelLowMedium = 2
plGaugePressurelevelMediumHigh = 3
plGaugePressurelevelHigh = 4

# StageStatus
stReady = 0
stDisabled = 1
stNotReady = 2
stGoing = 3
stMoving = 4
stWobbling = 5

# StageHolderType
hoNone = 0
hoSingleTilt = 1
hoDoubleTilt = 2
hoInvalid = 4
hoPolara = 5
hoDualAxis = 6

# IlluminationNormalization
nmSpotsize = 1
nmIntensity = 2
nmCondenser = 3
nmMiniCondenser = 4
nmObjectivePole = 5
nmAll = 6

# IlluminationMode
imNanoProbe = 0
imMicroProbe = 1

# DarkFieldMode
dfOff = 1
dfCartesian = 2
dfConical = 3

# CondenserMode
cmParallelIllumination = 0
cmProbeIllumination = 1

# ProjectionNormalization
pnmObjective = 10
pnmProjector = 11
pnmAll = 12

# ProjectionMode
pmImaging = 1
pmDiffraction = 2

# ProjectionSubMode
psmLM = 1
psmMi = 2
psmSA = 3
psmMh = 4
psmLAD = 5
psmD = 6

# LensProg
lpRegular = 1
lpEFTEM = 2

# ProjectionDetectorShift
pdsOnAxis = 0
pdsNearAxis = 1
pdsOffAxis = 2

# ProjDetectorShiftMode
pdsmAutoIgnore = 1
pdsmManual = 2
pdsmAlignment = 3

# HightensionState
htDisabled = 1
htOff = 2
htOn = 3

# InstrumentMode
InstrumentMode_TEM = 0
InstrumentMode_STEM = 1

# AcqShutterMode
AcqShutterMode_PreSpecimen = 0
AcqShutterMode_PostSpecimen = 1
AcqShutterMode_Both = 2

# AcqImageSize
AcqImageSize_Full = 0
AcqImageSize_Half = 1
AcqImageSize_Quarter = 2

# AcqImageCorrection
AcqImageCorrection_Unprocessed = 0
AcqImageCorrection_Default = 1

# AcqExposureMode
AcqExposureMode_None = 0
AcqExposureMode_Simultaneous = 1
AcqExposureMode_PreExposure = 2
AcqExposureMode_PreExposurePause = 3

# ProductFamily
ProductFamily_Tecnai = 0
ProductFamily_Titan = 1
