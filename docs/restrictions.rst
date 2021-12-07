.. _restrictions:

Restrictions
============

The restrictions listed here are issues with the scripting interface itself. `temscript` only provides Python bindings
to this scripting interface, thus these issues also occur using `temscript`. As there is no public list of known issues
with the scripting interfaces by FEI or Thermo Fisher Scientific themself, known issues are listed here for the user's
reference.

* Changing the projection mode from IMAGING to DIFFRACTION and back again changes the magnification in imaging
  mode (Titan 1.1).
* :attr:`Projection.Magnification` does not return the actual magnification, but always 0.0 (Titan 1.1)
* Setting the binning value for a CCD camera, changes the exposure time (Titan 1.1 with Gatan US1000 camera).
* Acquisition with changed exposure time with a CCD camera, are not always done with the new exposure time.
* :attr:`Illumination.IntensityLimitEnabled` raises exception when queried (Titan 1.1).
* :meth:`GoTo()` fails if movement is performed along multiple axes with speed keyword specified (internally the
  GoToWithSpeed method if the COM interface fails for multiple axes, Titan 1.1)
* Querying the attributes :attr:`STEMAcqParams.DwellTime`, :attr:`Illumination.StemMagnification`, and
  :attr:`Illumination.StemRotation` fails, if STEM is not available (Titan 1.1)
* If during a specimen holder exchange no holder is selected (yet), querying :attr:`Stage.Holder` fails (Titan 1.1).
