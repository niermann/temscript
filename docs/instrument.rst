.. currentmodule:: temscript

.. _instrument:

The COM interface
=================

The methods and classes directly represent the COM objects exposed by the *Scripting* interface.
The interface is described in detail in the scripting manual of your microscope
(usually in the file ``scripting.pdf`` located in the ``C:\Titan\Tem_help\manual`` or
``C:\Tecnai\tem_help\manual`` directories).

The manual is your ultimate reference, this documentation will only describe the
python wrapper to the COM interface.

Enumerations
^^^^^^^^^^^^

Many of the attributes return values from enumerations. These enumerations can be found in the
:mod:`temscript.enums` module.

.. versionchanged:: 2.0
    All methods of the COM interface now directly return the enumeration objects. The constants
    from temscript version 1.x are not defined anymore. The numerical values still can be accessed
    by querying the corresponding enum, e.g. ``psmSA`` corresponds to ``ProjectionSubMode.SA``.

Vectors
^^^^^^^

Some object attributes handle with two dimensional vectors (e.g. ``ImageShift``). These
attributes return ``(x, y)`` like tuples and expect iterable objects (``tuple``,
``list``, ...) with two floats when written (numpy arrays with two entries also work).

Interface classes
^^^^^^^^^^^^^^^^^

:class:`Instrument` - The entry point...
----------------------------------------

.. function:: GetInstrument()

    Creates a new instance of the :class:`Instrument` class. If your computer
    is not the microscope's PC or you don't have the *Scripting* option installed on
    your microscope, this method will raise an exception (most likely of the :exc:`OSError`
    type).

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

    .. attribute:: Camera

        (read) Instance of :class:`Camera` for fluscreen / plate camera control.

        .. versionadded:: 2.0

    .. attribute:: AutoNormalizeEnabled

        (read/write) *bool* Enable/Disable autonormalization procedures

    .. method:: NormalizeAll()

        Normalize all the lenses

        .. versionadded:: 2.0


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

        (read/write) *HighTensionState* State of accelerator

        .. versionchanged:: 2.0
            Returns *HighTensionState* instance instead of integer.

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

        (read/write) *IlluminationMode* Setting of minicondensor lens

        .. versionchanged:: 2.0
            Returns *IlluminationMode* instance instead of integer.

    .. attribute:: DFMode

        (read/write) *DarkFieldMode* Dark field mode.

        .. versionchanged:: 2.0
            Returns *DarkFieldMode* instance

    .. attribute:: DarkFieldMode

        (read/write) Alias of :attr:`DFMode`

    .. attribute:: BeamBlanked

        (read/write) *bool* Setting of beam blanker. The beam blanker puts a large current to
        the gun tilt coils to blank the beam before it is entering the condenser system.

    .. attribute:: CondenserStigmator

        (read/write) (X,Y) tuple in the range of -1.0 to +1.0 (logical units).

    .. attribute:: SpotSizeIndex

        (read/write) *int* The spot size (1-11).

    .. attribute:: SpotsizeIndex

        (read/write) Alias of :attr:`SpotSizeIndex`

    .. attribute:: Intensity

        (read/write) *float* Value corresponding to the C2-Knob setting, range
        between 0.0 to 1.0 (logical units)

    .. attribute:: IntensityZoomEnabled

        (read/write) *bool* Enable intensity zoom

    .. attribute:: IntensityLimitEnabled

        (read/write) *bool* Enable Intensity limit

        .. note:: Reading this property raises an exception (E_UNEXPECTED, "Catastrophic failure") on Titan 1.1

    .. attribute:: Shift

        (read/write) (X,Y) tuple of shift value (Meters). This corresponds to
        the *User (Beam) Shift* setting (which is displayed in logical units) in the
        *System Status* page. The scaling between the *Meters* and *logical units*
        depend on the calibration value stored in the aligment.

    .. attribute:: Tilt

        (read/write) Meaning depends on the setting of :attr:`DFMode`
            * in ``DarkFieldMode.CARTESIAN`` mode: (X, Y) tuple of shift value (Radians).
            * in ``DarkFieldMode.CONICAL`` mode: (theta, phi) tuple of angles (Radians).

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

        .. note::
            On Titan 1.1, reading this attribute fails, if STEM is not available. See :ref:`restrictions`.

    .. attribute:: StemRotation

        (read/write) *float* Rotation in STEM (radians).

        .. note::
            On Titan 1.1, reading this attribute fails, if STEM is not available. See :ref:`restrictions`.

    .. attribute:: CondenserMode

        (read/write) *CondenserMode* Condenser mode
        (Available only on Titan).

        .. versionchanged:: 2.0
            Returns *CondenserMode* instance

    .. attribute:: IlluminatedArea

        (read/write) *float* Illuminated area (meters? Is diameter meant? still to check). Requires parallel
        condensor mode.
        (Available only on Titan and only in `CondenserMode.PARALLEL` mode).

    .. attribute:: ProbeDefocus

        (read/write) *float* Probe defocus (meters) Requires probe condenser mode.
        (Available only on Titan and only in `CondenserMode.PROBE` mode).

    .. attribute:: ConvergenceAngle

        (read/write) *float* Convergence angle (radians) Requires probe condenser mode.
        (Available only on Titan and only in `CondenserMode.PROBE` mode).

    .. method:: Normalize(mode)

        Normalizes condenser lenses. *norm* specifies what elements to normalize, see *IlluminationNormalization*


:class:`Projection` - Projective system
---------------------------------------

.. class:: Projection

    Depending on the mode the microscope is in not all properties are
    accessable at all times (see scripting manual for details).

    .. attribute:: Mode

        (read/write) *ProjectionMode* Mode

        .. versionchanged:: 2.0
            Returns *ProjectionMode* instance instead of integer.

        .. note::
            On Titan 1.1 software changing the mode from IMAGING to DIFFRACTION and back again changes the
            magnification. See :ref:`restrictions`.

    .. attribute:: SubMode

        (read) *ProjectionSubMode* SubMode

        .. versionchanged:: 2.0
            Returns *ProjectionSubMode* instance instead of integer.

    .. attribute:: SubModeString

        (read) *str* Textual description of :attr:`Submode`.

    .. attribute:: LensProgram

        (read/write) *LensProg* Lens program

        .. versionchanged:: 2.0
            Returns *LensProg* instance instead of integer.

    .. attribute:: Magnification

        (read) *float* Magnification as seen be plate camera.
        Use :attr:`MagnificationIndex` to change.

        .. note::
            On Titan 1.1 software this property reads 0.0 regardless of used mode. See :ref:`restrictions`.

    .. attribute:: MagnificationIndex

        (read/write) *int* Magnification setting

    .. attribute:: ImageRotation

        (read) *float* Rotation of image/diffraction pattern with respect
        to specimen (radians)

    .. attribute:: DetectorShift

        (read/write) *ProjectionDetectorShift* Set shift of diffraction pattern to specified axis.

        .. versionchanged:: 2.0
            Returns *ProjectionDetectorShift* instance instead of integer.

    .. attribute:: DetectorShiftMode

        (read/write) *ProjDetectorShiftMode* Shift mode

        .. versionchanged:: 2.0
            Returns *ProjDetectorShiftMode* instance instead of integer.

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

        (read/write) *int* Camera length setting

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

        (read/write) *int* Corresponds to :attr:`MagnificationIndex` or
        :attr:`CameraLengthIndex` depending on mode.

    .. attribute:: SubModeMinIndex

        (read) *int* Smallest projection index of current submode.

    .. attribute:: SubModeMaxIndex

        (read) *int* Largest projection index of current submode.

    .. method:: ResetDefocus()

        Sets the :attr:`Defocus` of the current focus setting to zero (does not
        actually change the focus).

    .. method:: ChangeProjectionIndex(steps)

        Changes the current :attr:`ProjectionIndex` by *steps*.

    .. method:: Normalize(norm)

        Normalize projection system. *norm* specifies what elements to normalize, see *ProjectionNormalization*


:class:`Stage` - Stage control
------------------------------

.. class:: Stage

    .. attribute:: Status

        (read) *StageStatus* Status of the stage

        .. versionchanged:: 2.0
            Returns *StageStatus* instance instead of integer.

    .. attribute:: Position

        (read) Current position of stage. The function returns a ``dict``
        object with the values of the individual axes ('x', 'y', 'z', 'a', and 'b').

    .. attribute:: Holder

        (read) *StageHolderType* Type of holder

        .. versionchanged:: 2.0
            Returns *StageHolderType* instance instead of integer.

    .. method:: AxisData(axis)

        Returns tuple with information about that axis. Returned tuple
        is of the form (*min*, *max*, *unit*), where *min* is the minimum
        value, *max* the maximum value of the particular axis, and *unit* is
        a string containing the unit the axis is measured in (either 'meters' or
        'radians'). The *axis* must be one of the axes ('x', 'y', 'z', 'a', or 'b').

    .. method:: GoTo(x=None, y=None, z=None, a=None, b=None, speed=None)

        Moves stage to indicated position. Stage is only moved along
        the axes that are not ``None``.

        Optionally the keyword *speed* can be given, which allows to set the
        speed of the movement. 1.0 correspond to the default speed.

        .. note::
            At least with Titan 1.1 software, moving the stage along multiple axes with *speed* keyword set
            fails. Thus movement with *speed* set, must be done along a single axis only. See :ref:`restrictions`.

        .. versionchanged:: 1.0.10
            "speed" keyword added.

        .. versionchanged:: 2.0
            Internally the ``GoToWithSpeed`` method is used, when the *speed* keyword is given. Previous to version 2.0,
            the ``GoToWithSpeed`` method was only used if the *speed* keyword was different from 1.0.

    .. method:: MoveTo(x=None, y=None, z=None, a=None, b=None)

        Moves stage to indicated position. Stage is only moved along
        the axes that are not ``None``. In order to avoid pole-piece
        touch, the movement is carried out in the following order:

            b->0; a->0; z->Z; (x,y)->(X,Y); a->A; b->B

        .. versionchanged:: 2.0
            Invalid keywords raise ValueError (instead of TypeError)


Vacuum related classes
----------------------

.. class:: Vacuum

    .. attribute:: Status

        (read) *VacuumStatus* Status of the vacuum system

        .. versionchanged:: 2.0
            Returns *VacuumStatus* instance instead of integer.

    .. attribute:: PVPRunning

        (read) *bool* Whether the prevacuum pump is running

    .. attribute:: ColumnValvesOpen

        (read/write) *bool* Status of column valves

    .. attribute:: Gauges

        (read) List of :class:`Gauge` objects

    .. method:: RunBufferCycle()

        Runs a buffer cycle.


.. class:: Gauge

    .. attribute:: Name

        (read) *str* Name of the gauge

    .. attribute:: Status

        (read) *GaugeStatus* Status of the gauge

        .. versionchanged:: 2.0
            Returns *GaugeStatus* instance instead of integer.

    .. attribute:: Pressure

        (read) *float* Last measured pressure (Pascal)

    .. attribute:: PressureLevel

        (read) *GaugePressureLevel* Level of the pressure

        .. versionchanged:: 2.0
            Returns *GaugePressureLevel* instance instead of integer.

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

    .. attribute:: StemAcqParams

        (read/write) *STEMAcqParams* Acquisition parameters for STEM acquisition.

        In the original Scripting interface the STEM acquisition parameters are
        read/write on the detectors collection returned by the *Detectors* attribute.
        obtained via the list of detectors returned by the Acquisition instance.

        In version 1.X of the temscript adapter, this parameters were set via the STEMDetector
        instances itself, however the setting was common to all detectors.

        .. versionadded:: 2.0

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

        (read) *str* Name of CCD camera

    .. attribute:: Height

        (read) *int* Height of camera (pixels)

    .. attribute:: Width

        (read) *int* Width of camera (pixels)

    .. attribute:: PixelSize

        (read) (X, Y)-Tuple with physical pixel size (Manual says nothing about units, seems to be meters)

    .. attribute:: Binnings

        (read) List with supported binning values.

        .. versionchanged:: 2.0
            This attribute now returns a list of int (instead of a numpy array).

    .. attribute:: ShutterModes

        (read) List with supported shutter modes (see *AcqShutterMode* enumeration).

        .. versionchanged:: 2.0
            This attribute now returns a list of AcqShutterMode (instead of a numpy array).

    .. attribute:: ShutterMode

        (read/write) *AcqShutterMode* Selected shutter mode.

        .. versionchanged:: 2.0
            Returns *AcqShutterMode* instance instead of integer.


.. class:: CCDAcqParams

    .. attribute:: ImageSize

        (read/write) *AcqImageSize* Camera area used.

        .. versionchanged:: 2.0
            Returns *AcqImageSize* instance instead of integer.

    .. attribute:: ExposureTime

        (read/write) *float* Exposure time (seconds)

        .. note::
            On Titan 1.1 software images acquired after setting this property might not be acquired with the new
            setting, even though this property reflects the new value when read. See :ref:`restrictions`.

    .. attribute:: Binning

        (read/write) *int* Binning value

        .. note::
            On Titan 1.1 software setting this property also changes the exposure time. See :ref:`restrictions`.

    .. attribute:: ImageCorrection

        (read/write) *AcqImageCorrection* Correction mode.

        .. versionchanged:: 2.0
            Returns *AcqImageCorrection* instance instead of integer.

    .. attribute:: ExposureMode

        (read/write) *AcqExposureMode* Exposure mode.

        .. versionchanged:: 2.0
            Returns *AcqExposureMode* instance instead of integer.

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

        Parameters for STEM acquisition as instance of :class:`STEMAcqParams`. The
        acquisition parameters of all STEM detectors are identical, so this attribute
        will return the same instance for all detectors.

        .. deprecated:: 2.0

            Use the :attr:`StemAcqParams` attribute of the :class:`Acquisition` to set the parameters
            for STEM acqisition.


.. class:: STEMDetectorInfo

    .. attribute:: Name

        (read) *str* Name of detector camera

    .. attribute:: Brightness

        (read/write) *float* Brightness setting of the detector.

    .. attribute:: Contrast

        (read/write) *float* Contrast setting of the detector.

    .. attribute:: Binnings

        (read) List with supported binning values.

        .. versionchanged:: 2.0
            This attribute now returns a list of int (instead of a numpy array).


.. class:: STEMAcqParams

    .. attribute:: ImageSize

        (read/write) *AcqImageSize* Area of scan

        .. versionchanged:: 2.0
            Returns *AcqImageSize* instance instead of integer.

    .. attribute:: DwellTime

        (read/write) *float* Dwell time (seconds)

        .. note::
            On Titan 1.1, reading this attribute fails, if STEM is not available. See :ref:`restrictions`.

    .. attribute:: Binning

        (read/write) *int* Binning value


.. class:: AcqImage

    .. attribute:: Name

        (read) *unicode* Name of camera/detector

    .. attribute:: Height

        (read) *int* Height of acquired data array (pixels)

    .. attribute:: Width

        (read) *int* Width of acquired data array (pixels)

    .. attribute:: Depth

        (read) *int* Unsure: something like dynamic in bits, but not
        correct on our microscope.

    .. attribute:: Array

        (read) *numpy.ndarray* Acquired data as numpy array object.


Fluscreen and plate camera
--------------------------

.. class:: Camera

    Fluorescent screen and plate camera related methods.

    Since the plate camera is not supported anymore on newer Titans most of the methods
    of the Camera class are meaningless. Nevertheless, the attributes :attr:`ScreenCurrent`
    :attr:`MainScreen`, and :attr:`IsSmallScreenDown` still are usefull for fluscreen control.

    .. versionadded:: 2.0

    .. attribute:: Stock

        (read) *int* Number of plates still on stock

    .. attribute:: MainScreen

        (read/write) *ScreenPosition* Position of the fluscreen.

    .. attribute:: IsSmallScreenDown

        (read) *bool* Whether the focus screen is down.

    .. attribute:: MeasuredExposureTime

        (read) *float* Measured exposure time (seconds)

    .. attribute:: FilmText

        (read/write) *str* Text on plate. Up to 96 characters long.

    .. attribute:: ManualExposureTime

        (read/write) *float* Exposure time for manual exposures (seconds)

    .. attribute:: PlateuMarker

        (read/write) *bool*

        .. note:: Undocumented property

    .. attribute:: ExposureNumber

        (read/write) *int* Exposure number. The number is given as a 5 digit number
        plus 100000 * the ASCII code of one of the characters '0' to '9' or 'A' to 'Z'.

    .. attribute:: Usercode

        (read/write) *str* Three letter user code displayed on plate.

    .. attribute:: ManualExposure

        (read/write) *bool* Whether the `ManualExposureTime` will be used for plate exposure.

    .. attribute:: PlateLabelDataType

        (read/write) *PlateLabelDateFormat* Format of the date displayed on plate

    .. attribute:: ScreenDim

        (read/write) *bool* Whether the computer monitor is dimmed

    .. attribute:: ScreenDimText

        (read/write) *str* Test displayed when the computer monitor is dimmed.

    .. attribute:: ScreenCurrent

        (read) *float* The current measured on the flu screen (Amperes)

    .. method:: TakeExposure()

        Take single plate exposure.


Miscellaneous classes
---------------------

.. class:: InstrumentModeControl

    .. attribute:: StemAvailabe

        (read) *bool* Quite self decribing attribute

    .. attribute:: InstrumentMode

        (read/write) *InstrumentMode* TEM or STEM mode

        .. versionchanged:: 2.0
            Returns *InstrumentMode* instance instead of integer.


.. class:: BlankerShutter

    .. attribute:: ShutterOverrideOn

        (read/write) *bool* Overrides shutter control.

        .. warning::

            From the manual: If this override is on, there is no way to
            determine externally, that the override shutter is the active.
            So **always** reset this value from script, when finished.


.. class:: Configuration

    .. attribute:: ProductFamily

        (read) *ProductFamily* Microscope type

        .. versionchanged:: 2.0
            Returns *ProductFamily* instance instead of integer.


