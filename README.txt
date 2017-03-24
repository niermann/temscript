-- About ----------------------------------------------------------

The temscript module provides a Python wrapper for the scripting 
adapter of FEI microscopes (Tecnai & Titan). The functionality is
limited to the functionality of the scripting adapter. However,
not all functions are implemented in temscript yet. For more information
about TEM scripting see the documentation accompanying your microscope.

The scripting adapter can also be used from python using the win32com 
package. However, the win32com package (at least when tried out) uses 
tuples to copy the acquired image data (internally transmitted between
the COM-aware applications as SafeArray). This turned out to be really
slow for for 2Kx2K images. I never got it to work using the comtypes package.
Thus I decided to write the wrapper on my own, which then will return 
SafeArrays as numpy ndarray objects.

-- Building -------------------------------------------------------

Requirements:
    Python (tested with 2.7)
    Numpy (tested with 1.6)
    Sphinx (only for building documentation, tested with 1.1.3)
    A compiler (tested with MS Visual Studio 8/10)
    FEI Microscope's scripting adapter DLL. On a Titan V1.1 PC typically located in
        C:\Titan\Scripting\stdscript.dll

Alternatively, use the Anaconda python distribution (you still need
the compiler though)
    Tested with Python 3.4.3|Anaconda 2.3.0 (32-bit)
    Tested with Python 2.7.11|Anaconda 2.4.1 (32-bit)

Install your own microscope's scripting adapters type library:
    1) Copy your version of the scripting adapter's stdscript.dll into 
    to the _temscript_module subdirectory

Simply execute from the command line (assuming you have your python 
interpreter in the path):
    python setup.py build

-- Installing -----------------------------------------------------

You might need Adminstrator privileges to do this. Simply execute
from the command line (assuming you have your python interpreter 
in the path):
    python setup.py install

-- Supported functions --------------------------------------------

Relative to Titan V1.1 scripting adapter:
    Projection: complete
    Stage: Undocumented GotoWithSpeed() is missing
    Configuration: complete
    Acquisition: complete
    AcqImage: complete (AsSafeArray named Array)
    CCDCamera: complete
    CCDCameraInfo: complete
    CCDAcqParams: complete
    STEMDetector: complete (but untested)
    STEMAcqParams: complete (but untested)
    STEMDetectorInfo: complete (but untested)
    Camera: missing
    Gauge: complete
    Vacuum: complete
    UserButton: missing
    AutoLoader: missing
    TemperatureControl: missing
    Illumination: complete
    Instrument: ReportError and functions to acquire missing interfaces are missing 

-- Copyright & Disclaimer -----------------------------------------

Copyright (c) 2012-2017 by Tore Niermann
Contact: niermann (at) physik.tu-berlin.de

All product and company names are trademarks or registered trademarks 
of their respective holders. Use of them does not imply any affiliation
with or endorsement by them.

temscript is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
LICENCE.txt file for any details.

All product and company names are trademarks or registered trademarks of
their respective holders. Use of them does not imply any affiliation 
with or endorsement by them. 
