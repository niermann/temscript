__all__ = ("version", "GetInstrument")

# Set temscript version string
version = "1.0.5"

# Import COM bridging code
try:
    from _temscript import *

except ImportError:
    def GetInstrument():
        """Returns Instrument instance."""
        raise RuntimeError("temscript microscope API is not accessible")

    class Stage:
        pass

    class CCDCamera:
        pass

    class CCDCameraInfo:
        pass

    class CCDAcqParams:
        pass

    class STEMDetector:
        pass

    class STEMDetectorInfo:
        pass

    class STEMAcqParams:
        pass

    class AcqImage:
        pass

    class Acquisition:
        pass

    class Gauge:
        pass

    class Vacuum:
        pass

    class Configuration:
        pass

    class Projection:
        pass

    class Illumination:
        pass

    class Gun:
        pass

    class BlankerShutter:
        pass

    class InstrumentModeControl:
        pass

    class Instrument:
        pass
