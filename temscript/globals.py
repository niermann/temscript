__all__ = ("version", "GetInstrument")

# Set temscript version string
version = "1.0.5"

# Import COM bridging code
try:
    import _temscript
    GetInstrument = _temscript.GetInstrument

except ImportError:
    def GetInstrument():
        """Returns Instrument instance."""
        raise RuntimeError("temscript microscope API is not accessible")
