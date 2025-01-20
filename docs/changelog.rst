Changelog
=========

Version 2.1.0
^^^^^^^^^^^^^

* Changed default apartment model to COINIT_APARTMENTTHREADED to increase compatibility with comtypes
* COM initialization respects setting from sys.coinit_flags

Version 2.0.1
^^^^^^^^^^^^^

* Added Talos as ProductFamily
* Added more graceful behavior for unsupported ProductFamily query and unknown future families.
* Added column valves state to Microscope classes.

Version 2.0.0
^^^^^^^^^^^^^

* C++ adapter removed, COM interface no directly accessed using ``ctypes``
* Raised required minimum Python version to 3.4 (dropped support of Python 2.X)
* More extensive documentation of the high level interfaces and the temscript server
* Documentation of known issues of the original scripting interface
* Support of the fluorescent screen
* Separation of STEM detectors and CCD cameras in high level interface
* Deprecation of the methods 'get_detectors', 'get_detector_param', 'set_detector_params', and 'get_optics_state' of
  'Microscope' and related classes. See docs for further details.
* Deprecation of the property 'AcqParams' of 'STEMDetector'. See docs for further details.
* Deprecation of the use of 'speed' and 'method' keywords in position dictionary of the 'set_stage_position' method.
* Abstract base class for high level interface
* Test scripts
* More illumination related functions
* TEM/STEM mode control
* Several small improvements and fixes

Version 1.0.10
^^^^^^^^^^^^^^

* Speed keyword added Stage.Goto / Microscope.set_stage_position
* A lot of properties added to Microscope API (DiffShift, ObjStig, CondStig, Projection Mode / SubMode, Magnification, Normalization)
* More properties returned by Microscope.get_optics_state
* Timeout for RemoteMicroscope
* Lots of fixes

Version 1.0.9
^^^^^^^^^^^^^

* Normalization methods in new interface.
* Projective system settings in new interface.

Version 1.0.7
^^^^^^^^^^^^^

Started new interface (with client/server support).

Version 1.0.5
^^^^^^^^^^^^^

* Small fixes
* Clarified license: 3-clause BSD
* Compatibility to Py3K and anaconda distribution

Version 1.0.3
^^^^^^^^^^^^^

* Fixed some small things

Version 1.0.2
^^^^^^^^^^^^^

* Renamed project to temscript.
* Created documentation.

Version 1.0.1
^^^^^^^^^^^^^

* Fixed memory leak related to safearray handling

Version 1.0.0
^^^^^^^^^^^^^

* Initial release
