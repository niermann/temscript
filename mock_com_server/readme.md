Building
--------

Add to project settings:

Linker -> Input -> Module Definition File:
TemscriptMockObject.def

Build -> TemscriptMockObject.dll

Installation
------------

Register as COM object (exec as admin):
regsvr32 TemscriptMockObject.dll

For unregistration (after testing) use:
regsvr32 /u TemscriptMockObject.dll

Pre-build files
---------------
The provided DLL (TemscriptMockObject.dll) is built for 64bit Windows (and not for 32 bit).
