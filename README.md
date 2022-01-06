# About

The ``temscript`` package provides a Python wrapper for the scripting
interface of Thermo Fisher Scientific and FEI microscopes. The functionality is
limited to the functionality of the original scripting interface. For detailed information
about TEM scripting see the documentation accompanying your microscope.

The ``temscript`` package provides two interfaces to the microsope. The first one
corresponds directly to the COM interface. The other interface is a more high level interface.
Within the ``temscript`` package three implementation for the high level interface are provided,
one for running scripts directly on the microscope PC, one to run scripts remotely over network, and
finally a dummy implementation for offline development & testing exists.

Currently the ``temscript`` package requires Python 3.4 or higher. The current plan is to keep the minimum
supported Python version at 3.4, since this is the latest Python version supporting Windows XP.

The sources can be found on GitHub: https://github.com/niermann/temscript

# Documentation

The documentation of the latest version can be found at:

https://temscript.readthedocs.io/

# Installation

Requirements:
* Python >= 3.4 (tested with 3.4)
* Numpy (tested with 1.9)
* Sphinx (only for building documentation, tested with 1.6)

On all platforms the dummy and remote high level interfaces are provided. 
On Windows platforms the package provides the Python wrapper
to the scripting COM interface. However, trying to instantiate this wrapper
will fail, if the scripting COM classes are not installed locally.

### Installation from wheels file (using pip)

This assumes you have downloaded the wheels file <downloaded-wheels-file>.whl 

Execute from the command line (assuming you have your python interpreter in the path, this might require superuser or 
administrator privileges):
    
    python3 -m pip install --upgrade pip
    python3 -m pip install <downloaded-wheels-file>.whl

### Installation from sources (using pip)

This assumes you have downloaded and extracted the sources into the directory <source_directory> (alternative have
cloned the sources from GitHub into <source_directory>). 

Execute from the command line (assuming you have your python interpreter in the path, this might require superuser or 
administrator privileges):
    
    python3 -m pip install --upgrade pip
    python3 -m pip install <source_directory>

### Installation from sources (using distutils)

This assumes you have downloaded and extracted the sources into the directory <source_directory> (alternative have
cloned the sources from GitHub into <source_directory>). 

Execute from the command line (assuming you have your python interpreter in the path, this might require superuser or 
administrator privileges):
    
    cd <source_directory>
    python3 setup.py install

# Supported functions of the COM interface

Relative to Titan V1.1 scripting adapter:
* Projection: complete
* Stage: complete
* Configuration: complete
* Acquisition: complete
* AcqImage: complete
* CCDCamera: complete
* CCDCameraInfo: complete
* CCDAcqParams: complete
* STEMDetector: complete (but untested)
* STEMAcqParams: complete (but untested)
* STEMDetectorInfo: complete (but untested)
* Camera: complete
* Gauge: complete
* Vacuum: complete
* UserButton: missing
* AutoLoader: missing
* TemperatureControl: missing
* Illumination: complete

# Copyright & Disclaimer

Copyright (c) 2012-2021 by Tore Niermann
Contact: tore.niermann (at) tu-berlin.de

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
