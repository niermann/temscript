The classical interface
=======================

.. module:: temscript

.. function:: GetInstrument()

    Creates a new instance of the :class:`Instrument` class. If your computer
    is not the microscope's PC or you don't have the *Scripting* option installed on
    your microscope, this method will raise an exception (most likely of the :exc:`COMError`
    type).

.. exception:: COMError

    Exceptions of this type are raised, when something with COM libary or the communication
    with the microscope server failed. The value of the exception consists of a
    tuple containing the error code and a textual representation of the error (most likely
    just something like "HRESULT=0xXXXXXXXX").

:class:`Instrument` - The entry point...
----------------------------------------

.. class:: Instrument

    Top level object representing the microscope. Use the :func:`GetInstrument`
    function to create an instance of this class.

    .. attribute:: Gun

        (read) Instance of :class:`Gun` for access to gun related functionalities

    .. attribute:: Illumination

        (read) Instance of :class:`Illumination` for access to illumination
        system and condenser related functionalities

    .. attribute:: Projection

        (read) Instance of :class:`Projection` for access to projection
        system related functionalities

    .. attribute:: Stage

        (read) Instance of :class:`Stage` for stage control

    .. attribute:: Acquisition

        (read) Instance of :class:`Acquisition` for image acquisition

    .. attribute:: Vacuum

        (read) Instance of :class:`Vacuum` for access to vacuum system related
        functionalities

    .. attribute:: InstrumentModeControl

        (read) Instance of :class:`InstrumentModeControl` for TEM/STEM switching.

    .. attribute:: BlankerShutter

        (read) Instance of :class:`BlankerShutter` for blanker control.

    .. attribute:: Configuration

        (read) Instance of :class:`Configuration` for microscope identification.

    .. attribute:: AutoNormalizeEnabled

        (read/write) *bool* Enable/Disable autonormalization procedures

:class:`Gun` - Gun stuff
------------------------

.. class:: Gun

    .. attribute:: Tilt

        (read/write) (X,Y) tuple in the range of -1.0 to +1.0 (logical units).
        This attribute is inaccessable when the beamblanker (see
        :class:`Illumination`) is active.

    .. attribute:: Shift

        (read/write) (X,Y) tuple in the range of -1.0 to +1.0 (logical units).

    .. attribute:: HTState

        (read/write) One of these
            * ``htDisabled``
            * ``htOff``
            * ``htOn``

    .. attribute:: HTValue

        (read/write) *float* Current acceleration voltage (Volts)

        .. warning::

            Be careful when writing this attribute, it allows you to change the high tension.

    .. attribute:: HTMaxValue

        (read) *float* Max. HT Value of the microscope (Volts)

:class:`Illumination` - Condenser sytem
---------------------------------------

.. class:: Illumination

    The functionality of some methods/attributes depend on the
    mode the illumination is in (see the manual for details).

    .. attribute:: Mode

        (read/write) Setting of minicondensor lens
            * ``imNanoProbe``
            * ``imMicroProbe``

    .. attribute:: DFMode

        (read/write) Dark field mode:
            * ``dfOff``
            * ``dfCartesian``
            * ``dfConical``

    .. attribute:: DarkFieldMode

        (read/write) Alias of :attr:``DFMode``

    .. attribute:: BeamBlanked

        (read/write) *bool* Setting of beam blanker. The beam blanker puts a large current to
        the gun tilt coils to blank the beam before it is entering the condenser system.

    .. attribute:: CondenserStigmator

        (read/write) (X,Y) tuple in the range of -1.0 to +1.0 (logical units).
    .. attribute: SpotsizeIndex

        (read/write) *long* The spot size (1-11).

    .. attribute: Intensity

        (read/write) *float* Value corresponding to the C2-Knob setting, range
        between 0.0 to 1.0 (logical units)

    .. attribute: IntensityZoomEnabled

        (read/write) *bool* Enable intensity zoom

    .. attribute:

        (read/write) *bool* Enable Intensity limit

    .. attribute:: Shift

        (read/write) (X,Y) tuple of shift value (Meters). This corresponds to
        the *User (Beam) Shift* setting (which is displayed in logical units) in the
        *System Status* page. The scaling between the *Meters* and *logical units*
        depend on the calibration value stored in the aligment.

    .. attribute:: Tilt

        (read/write)
            * in ``dfCartesian`` mode: (X,Y) tuple of shift value (Radians).
            * in ``dfConical`` mode: (theta,phi) tuple of angles (Radians).

        This corresponds to the *DF Tilt* setting (which is displayed in logical units) in the
        *System Status* page. The scaling between the *Radians* and the *logical units*
        depend on the calibration value stored in the aligment.

    .. attribute:: RotationCenter

        (read/write) (X,Y) tuple of tilt value (Radians). This corresponds to the
        *Rot. Center* setting (which is displayed in logical units) in the
        *System Status* page. The scaling between the *Radians* and the *logical units*
        depend on the calibration value stored in the aligment.

    .. attribute:: StemMagnification

        (read/write) *float* Magnification in STEM. As the magnification must be
        one of the discret values (as displayed on the micrsocope), the value is
        rounded to the next available value on write.

    .. attribute:: StemRotation

        (read/write) *float* Rotation in STEM (radians).

    .. attribute:: CondenserMode

        (read/write) One of
            * ``cmParallelIllumination``
            * ``cmProbeIllumination``

        (Available only on Titan).

    .. attribute:: IlluminatedArea

        (read/write) *float* Illuminated area (meters? Is diameter meant? still to check). Requires parallel
        condensor mode. (Available only on Titan).

    .. attribute:: ProbeDefocus

        (read/write) *float* Probe defocus (meters) Requires probe condensor mode.
        (Available only on Titan).

    .. attribute:: ConvergenceAngle

        (read/write) *float* Convergence angle (radians) Requires probe condensor mode.
        (Available only on Titan).

    .. method:: Normalize(mode)

        Normalizes condenser lenses. *mode* is one of
            * ``nmSpotsize``
            * ``nmIntensity``
            * ``nmCondenser``
            * ``nmMiniCondenser``
            * ``nmObjectivePole``
            * ``nmAll``

:class:`Projection` - Projective sytem
---------------------------------------

.. class:: Projection

    Depending on the mode the microscope is in not all properties are
    accessable at all times (see manual for details).

    .. attribute:: Mode

        (read/write) One of
            * ``pmImaging``
            * ``pmDiffraction``

    .. attribute:: SubMode

        (read) One of
            * ``psmLM``
            * ``psmMi``
            * ``psmSA``
            * ``psmMh``
            * ``psmLAD``
            * ``psmD``

    .. attribute:: SubModeString

        (read) *unicode* Textual description of :attr:`Submode`.

    .. attribute:: LensProgram

        (read/write) One of
            * ``lpRegular``
            * ``lpEFTEM``

    .. attribute:: Magnification

        (read) *float* Magnification as seen be plate camera.
        Use :attr:`MagnificationIndex` to change.

    .. attribute:: MagnificationIndex

        (read/write) *long* Magnification setting

    .. attribute:: ImageRotation

        (read) *float* Rotation of image/diffraction pattern with respect
        to specimen (radians)

    .. attribute:: DetectorShift

        (read/write) Move image/diffraction pattern to detector. One of
            * ``pdsOnAxis``
            * ``pdsNearAxis``
            * ``pdsOffAxis``

    .. attribute:: DetectorShiftMode

        (read/write) One of
            * ``pdsmAutoIgnore``
            * ``pdsmManual``
            * ``pdsmAlignment``

    .. attribute:: Focus

        (read/write) *float* Focus setting relative to focus preset (logical units).
        Range -1.0 (underfocus) to +1.0 (overfocus).

    .. attribute:: Defocus

        (read/write) *float* Defocus (meters), relative to defocus set with :func:`ResetDefocus`.

    .. attribute:: ObjectiveExcitation

        (read) *float* Objective lens excitation in percent.

    .. attribute:: CameraLength

        (read) *float* Camera length as seen by plate camera (meters). Use
        :attr:`CameraLengthIndex` to change.

    .. attribute:: CameraLengthIndex

        (read/write) *long* Camera length setting

    .. attribute:: ObjectiveStigmator

        (read/write) (X,Y) tuple in the range of -1.0 to +1.0 (logical units).

    .. attribute:: DiffractionStigmator

        (read/write) (X,Y) tuple in the range of -1.0 to +1.0 (logical units).

    .. attribute:: DiffractionShift

        (read/write) (X,Y) tuple of shift value (radians). This corresponds to
        the *User Diffraction Shift* setting (which is displayed in logical units) in the
        *System Status* page. The scaling between the *radians* and *logical units*
        depend on the calibration value stored in the aligment.

    .. attribute:: ImageShift

        (read/write) (X,Y) tuple of shift value (meters). This corresponds to
        the *User (Image) Shift* setting (which is displayed in logical units) in the
        *System Status* page. The scaling between the *Meters* and *logical units*
        depend on the calibration value stored in the aligment.

    .. attribute:: ImageBeamShift

        (read/write) (X,Y) tuple of shift value (meters). Shifts image and while compensating
        for the apparent beam shift.
        From the manual: Don't intermix :attr:`ImageShift` and :attr:`ImageBeamShift`, reset
        one of them ot zero before using the other.

    .. attribute:: ImageBeamTilt

        (read/write) (X,Y) tuple of tilt value. Tilts beam and compensates tilt by diffraction
        shift.

    .. attribute:: ProjectionIndex

        (read/write) *long* Corresponts to :attr:`MagnificationIndex` or
        :attr:`CameraLengthIndex` depending on mode.

    .. attribute:: SubModeMinIndex

        (read) *long* Smallest projection index of current submode.

    .. attribute:: SubModeMaxIndex

        (read) *long* Largest projection index of current submode.

    .. method:: ResetDefocus()

        Sets the :attr:`Defocus` of the current focus setting to zero (does not
        actually change the focus).

    .. method:: ChangeProjectionIndex(steps)

        Changes the current :attr:`ProjectionIndex` by *steps*.

    .. method:: Normalize(norm)

        Normalize projection system. *norm* is one of
            * ``pnmObjective``
            * ``pnmProjector``
            * ``pnmAll``

:class:`Stage` - Stage control
------------------------------

.. class:: Stage

    .. attribute:: Status

        (read) One of
            * ``stReady``
            * ``stDisabled``
            * ``stNotReady``
            * ``stGoing``
            * ``stMoving``
            * ``stWobbling``

    .. attribute:: Position

        (read) Current position of stage. The function returns a ``dict``
        object with the values of the indiviual axes.

    .. attribute:: Holder

        (read) Type of holder. One of
            * ``hoNone``
            * ``hoSingleTilt``
            * ``hoDoubleTilt``
            * ``hoInvalid``
            * ``hoPolara``
            * ``hoDualAxis``

    .. method:: AxisData(axis)

        Returns tuple with information about that axis. Returned tuple
        is of the form (*min*, *max*, *unit*), where *min* is the minimum
        value, *max* the maximim value of the particular axis, and *unit* is
        a string containing the unit the axis is measured in (either 'meters' or
        'radians'). The *axis* must be of string type and contain
        either 'x', 'y', 'z', 'a', or 'b'.

    .. method:: GoTo(x=None, y=None, z=None, a=None, b=None)

        Moves stage to indicated position. Stage is only moved along
        the axes that are not ``None``.

    .. method:: MoveTo(x=None, y=None, z=None, a=None, b=None)

        Moves stage to indicated position. Stage is only moved along
        the axes that are not ``None``. In order to avoid pole-piece
        touch, the movement is carried out in the following order:

            b->0; a->0; z->Z; (x,y)->(X,Y); a->A; b->B

Vacuum related classes
----------------------

.. class:: Vacuum

    .. attribute:: Status

        (read) One of:
            * ``vsUnknown``
            * ``vsOff``
            * ``vsCameraAir``
            * ``vsBusy``
            * ``vsReady``
            * ``vsElse``

    .. attribute:: ColumnValvesOpen

        (read/write) *bool* Status of column valves

    .. attribute:: PVPRunning

        (read) *bool* Whether the prevacuum pump is running

    .. attribute:: Gauges

        (read) List of :class:`Gauge` objects

    .. method:: RunBufferCycle()

        Runs a buffer cycle.

.. class:: Gauge

    .. attribute:: Name

        (read) *unicode* Name of the gauge

    .. attribute:: Status

        (read) One of
            * ``gsUndefined``
            * ``gsUnderflow``
            * ``gsOverflow``
            * ``gsInvalid``
            * ``gsValid``

    .. attribute:: Pressure

        (read) *float* Last measured pressure (Pascal)

    .. attribute:: PressureLevel

        (read) One of
            * ``plGaugePressurelevelUndefined``
            * ``plGaugePressurelevelLow``
            * ``plGaugePressurelevelLowMedium``
            * ``plGaugePressurelevelMediumHigh``
            * ``plGaugePressurelevelHigh``

    .. method:: Read()

        Read the pressure level. Call this before reading the value
        from :attr:`Pressure`.

Acquisition related classes
---------------------------

.. class:: Acquisition

    .. note::

        From the manual:
            * TIA must be running
            * After changing the detector selection in the UI you must
              reacquire a new :class:`Instrument` using the :func:`GetInstrument`
              function.
            * In order for detectors/cameras to be available, they must
              be selected in the UI.

    .. attribute:: Cameras

        (read) List of :class:`CCDCamera` objects.

    .. attribute:: Detectors

        (read) List of :class:`STEMDetector` objects.

    .. method:: AddAcqDevice(device)

        Adds *device* to the list active devices. *device* must be of
        type :class:`CCDCamera` or :class:`STEMDetector`.

    .. method:: AddAcqDeviceByName(deviceName)

        Adds device with name *deviceName* to the list active devices.

    .. method:: RemoveAcqDevice(device)

        Removes *device* to the list active devices. *device* must be of
        type :class:`CCDCamera` or :class:`STEMDetector`.

    .. method:: RemoveAcqDeviceByName(deviceName)

        Removes device with name *deviceName* to the list active devices.

    .. method:: RemoveAllAcqDevices()

        Clears the list of active devices.

    .. method:: AcquireImages()

        Acquires image from each active device, and returns them as list
        of :class:`AcqImage`.

.. class:: CCDCamera

    .. attribute:: Info

        Information about the camera as instance of :class:`CCDCameraInfo`

    .. attribute:: AcqParams

        Acquisition parameters of the camera as instance of :class:`CCDAcqParams`

.. class:: CCDCameraInfo

    .. attribute:: Name

        (read) *unicode* Name of CCD camera

    .. attribute:: Height

        (read) *long* Height of camera (pixels)

    .. attribute:: Width

        (read) *long* Width of camera (pixels)

    .. attribute:: PixelSize

        (read) (X, Y)-Tuple with physical pixel size (Manual says nothing about units, seems to be meters)

    .. attribute:: Binnings

        (read) *numpy.ndarray* with supported binning values.

    .. attribute:: ShutterModes

        (read) *numpy.ndarray* with supported shutter modes.
        See :attr:`ShutterMode` for possible values.

    .. attribute:: ShutterMode

        (read/write) One of
            * ``AcqShutterMode_PreSpecimen``
            * ``AcqShutterMode_PostSpecimen``
            * ``AcqShutterMode_Both``

.. class:: CCDAcqParams

    .. attribute:: ImageSize

        (read/write) One of
            * ``AcqImageSize_Full``
            * ``AcqImageSize_Half``
            * ``AcqImageSize_Quarter``

    .. attribute:: ExposureTime

        (read/write) *float* Exposure time (seconds)

    .. attribute:: Binning

        (read/write) *long* Binning value

    .. attribute:: ImageCorrection

        (read/write) One of
            * ``AcqImageCorrection_Unprocessed``
            * ``AcqImageCorrection_Default``

    .. attribute:: ExposureMode

        (read/write) One of
            * ``AcqExposureMode_None``
            * ``AcqExposureMode_Simultaneous``
            * ``AcqExposureMode_PreExposure``
            * ``AcqExposureMode_PreExposurePause``

    .. attribute:: MinPreExposureTime

        (read) *float* Smallest pre exposure time (seconds)

    .. attribute:: MaxPreExposureTime

        (read) *float* Largest pre exposure time (seconds)

    .. attribute:: MinPreExposurePauseTime

        (read) *float* Smallest pre exposure pause time (seconds)

    .. attribute:: MaxPreExposurePauseTime

        (read) *float* Largest pre exposure pause time (seconds)

    .. attribute:: PreExposureTime

        (read/write) *float* pre exposure time (seconds)

    .. attribute:: PreExposurePauseTime

        (read/write) *float* pre exposure pause time (seconds)

.. class:: STEMDetector

    .. attribute:: Info

        Information about the detector as instance of :class:`STEMDetectorInfo`

    .. attribute:: AcqParams

        Acquisition parameters of the detector as instance of :class:`STEMAcqParams`. The
        acquisition parameters of all STEM detectors are identical, so this attribute
        will return the same instance for all detectors.

        In the original Scripting interface the instance of the STEM acquisition parameters is
        obtained via the list of detectors returned by the Acquisition instance. In the temscript
        python interface, the parameter instance is obtained via the STEMDetector instances.
        However all detectors will haul the same parameter object.

.. class:: STEMDetectorInfo

    .. attribute:: Name

        (read) *unicode* Name of detector camera

    .. attribute:: Brightness

        (read/write) *float* Brightness setting of the detector.

    .. attribute:: Contrast

        (read/write) *float* Contrast setting of the detector.

    .. attribute:: Binnings

        (read) *numpy.ndarray* with supported binning values.

.. class:: STEMAcqParams

    .. attribute:: ImageSize

        (read/write) One of
            * ``AcqImageSize_Full``
            * ``AcqImageSize_Half``
            * ``AcqImageSize_Quarter``

    .. attribute:: DwellTime

        (read/write) *float* Dwell time (seconds)

    .. attribute:: Binning

        (read/write) *long* Binning value

.. class:: AcqImage

    .. attribute:: Name

        (read) *unicode* Name of camera/detector

    .. attribute:: Height

        (read) *long* Height of acquired data array (pixels)

    .. attribute:: Width

        (read) *long* Width of acquired data array (pixels)

    .. attribute:: Depth

        (read) *long* Unsure: something like dynamic in bits, but not
        correct on our microscope.

    .. attribute:: Array

        (read) *numpy.ndarray* Acquired data as array object.

Miscellaneous classes
---------------------

.. class:: InstrumentModeControl

    .. attribute:: StemAvailabe

        (read) *bool* Quite self decribing attribute

    .. attribute:: InstrumentMode

        (read/write) Possible values
            * ``InstrumentMode_TEM``
            * ``InstrumentMode_STEM``

.. class:: BlankerShutter

    .. attribute:: ShutterOverrideOn

        (read/write) *bool* Overrides shutter control.

        .. warning::

            From the manual: If this override is on, there is no way to
            determine externally, that the override shutter is the active.
            So **always** reset this value from script, when finished.

.. class:: Configuration

    .. attribute:: ProductFamily

        (read) Possible values
            * ``ProductFamily_Tecnai``
            * ``ProductFamily_Titan``

