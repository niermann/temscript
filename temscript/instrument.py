__all__ = ("version", "GetInstrument")

# Set temscript version string
version = "1.0.5"

# Import COM bridging code
try:
    from _temscript2 import *

except ImportError:
    def GetInstrument():
        """Returns Instrument instance."""
        raise RuntimeError("temscript microscope API is not accessible")

    class Instrument:
        pass

    class Acquisition:
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

