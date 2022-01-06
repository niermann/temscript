from abc import ABC, abstractmethod


def parse_enum(enum_type, item):
    """Try to parse *item* (string or integer) to enum *type*"""
    if isinstance(item, enum_type):
        return item
    try:
        return enum_type[item]
    except KeyError:
        return enum_type(item)


def set_attr_from_dict(obj, attr_name, mapping, key, ignore_errors=False):
    """
    Tries to set attribute *attr_name* of object *obj* with the value of *key* in the dictionary *map*.
    The item *key* is removed from the *map*.
    If no such *key* is in the dict, nothing is done.
    Any TypeErrors or ValueErrors are silently ignored, if *ignore_errors is set.

    Returns true is *key* was present in *map* and the attribute was successfully set. Otherwise False is returned.
    """
    try:
        value = mapping.pop(key)
    except KeyError:
        return False

    try:
        setattr(obj, attr_name, value)
    except (TypeError, ValueError):
        if ignore_errors:
            return False
        raise

    return True


def set_enum_attr_from_dict(obj, attr_name, enum_type, mapping, key, ignore_errors=False):
    """
    Tries to set enum attribute *attr_name* of object *obj* with the value of *key* in the dictionary *map*.
    The value is parsed to the *enum_type* (using `parse_enum` before the attribute is set).
    The item *key* is removed from the *map*.
    If no such *key* is in the dict nothing is done.
    Any TypeErrors or ValueErrors are silently ignored, if *ignore_errors is set.

    Returns true is *key* was present in *map* and the attribute was successfully set. Otherwise False is returned.
    """
    try:
        value = mapping.pop(key)
    except KeyError:
        return False

    try:
        value = parse_enum(enum_type, value)
    except (KeyError, ValueError):
        if ignore_errors:
            return False
        raise

    try:
        setattr(obj, attr_name, value)
    except (TypeError, ValueError):
        if ignore_errors:
            return False
        raise

    return True


# Allowed stage axes
STAGE_AXES = frozenset(('x', 'y', 'z', 'a', 'b'))


class BaseMicroscope(ABC):
    """
    Base class for Microscope classes. Do not use directly.
    """
    @abstractmethod
    def get_family(self):
        """Return product family (see :class:`ProductFamily`): "TITAN", "TECNAI", ..."""
        raise NotImplementedError

    @abstractmethod
    def get_microscope_id(self):
        """
        Return microscope ID.

        There is no way to read this via the scripting adapter directly, thus this method uses hostname instead.
        """
        raise NotImplementedError

    @abstractmethod
    def get_version(self):
        """
        Return version string for temscript.

        .. versionadded:: 1.0.8

        :return: String "major.minor.patchlevel"
        """
        raise NotImplementedError

    @abstractmethod
    def get_voltage(self):
        """
        Return acceleration voltage in kV.

        :return: Float with voltage
        """
        raise NotImplementedError

    @abstractmethod
    def get_vacuum(self):
        """
        Return status of the vacuum system. The method will return a dict with the following entries:

            * "status": Status of the vacuum system (see :class:`VacuumStatus`): "READY", "OFF", ...
            * "column_valves_open": Whether the column valves are currently open
            * "pvp_running": Whether the PVP is running
            * "gauges(Pa)": dict with Gauge values in Pascal (or the string "UNDERFLOW" or "OVERFLOW")

        .. versionchanged: 1.0.8
            Key of "gauges(Pa)" in the returned dict was changed from "gauges"
        """
        raise NotImplementedError

    @abstractmethod
    def get_stage_holder(self):
        """Return holder currently in stage (see :class:`StageHolderType`)"""
        raise NotImplementedError

    @abstractmethod
    def get_stage_status(self):
        """Return status of stage (see :class:`StageStatus`)"""
        raise NotImplementedError

    @abstractmethod
    def get_stage_limits(self):
        """
        Returns dictionary with min/max tuples for all holder axes.
        The tuples are the values, the axis names are the keys.
        For axes "x", "y", "z" the unit is meters
        For axes "a", "b" the unit is radians
        """
        raise NotImplementedError

    @abstractmethod
    def get_stage_position(self):
        """
        Returns dictionary with stage position (axes names are used as keys).
        For axes "x", "y", "z" the unit is meters
        For axes "a", "b" the unit is radians
        """
        raise NotImplementedError

    @abstractmethod
    def _set_stage_position(self, pos=None, method="GO", speed=None):
        raise NotImplementedError

    def set_stage_position(self, pos=None, method=None, speed=None, **kw):
        """
        Set new stage position.

        The new position can either be passed as dict `pos` or passed by keywords
        `x`, `y`, `z`, `a`, `b`. If both are present, the keywords override values from the dict.
        Only the axes are driven which are mentioned in the `pos` dict or by keywords.

        The optional keyword "speed" allows to set movement speed (only "GO" method). A speed of 1.0 corresponds
        to default speed.

        For axes "x", "y", "z" the unit is meters.
        For axes "a", "b" the unit is radians.

        There are two methods of movement:

            * "GO": Moves directly to new stage position (default)
            * "MOVE": Avoids pole piece touches, by first zeroing the
              angle, moving the stage than, and setting the angles again.

        .. versionchanged:: 1.0.10
            "speed" keyword added.

        .. deprecated::
            In versions < 2.0.0 the "speed" and "method" keywords could also be passed within the `pos` dictionary.
            This is usage is deprecated since 2.0.0, use the `speed` and `method` keywords instead.
        """
        pos = dict(pos) if pos is not None else dict()
        for key, value in kw.items():
            if key not in STAGE_AXES:
                raise AttributeError("Unknown keyword '%s'" % key)
            pos[key] = value
        if "speed" in pos:
            import warnings
            warnings.warn("Usage of the 'speed' key in the 'pos' dictionary is deprecated since version 2.0."
                          "Use the 'speed' keyword instead.", DeprecationWarning)
            if speed is None:
                speed = pos.pop('speed')
        if "method" in pos:
            import warnings
            warnings.warn("Usage of the 'method' key in the 'pos' dictionary is deprecated since version 2.0."
                          "Use the 'method' keyword instead.", DeprecationWarning)
            if method is None:
                method = pos.pop('method')
        if method is None:
            method = "GO"
        self._set_stage_position(pos, method=method, speed=speed)

    @abstractmethod
    def get_cameras(self):
        """
        Return dictionary with all available cameras. The method will return a dict, indexed by camera name, with
        another dict as values.

        For cameras the embedded dict will additionally have the following keys:

                * "type": "CAMERA"
                * "height": Height of the detector
                * "width": Width of the detector
                * "pixel_size(um)": Pixel size in micrometers
                * "binnings": List of supported binnings
                * "shutter_modes": List of supported shutter modes (see :class:`AcqShutterMode`)
                * "pre_exposure_limits(s)": Tuple with Min/Max values of pre exposure times in seconds
                * "pre_exposure_pause_limits(s)": Tuple with Min/Max values of pre exposure pause times in seconds

        For "STEM_DETECTOR" detectors the embedded dict will additionally have the following keys:

                * "binnings": List of supported binnings

        .. versionadded:: 2.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_stem_detectors(self):
        """
        Return dictionary with all available stem detectors. The method will return a dict, indexed by camera name, with
        another dict as values.

        The embedded dict will additionally have the following keys:

                * "type": "STEM_DETECTOR"
                * "binnings": List of supported binnings

        .. versionadded:: 2.0
        """
        raise NotImplementedError

    def get_detectors(self):
        """
        Return dictionary with all available detectors.

        The returned dictionary is the combination of the dicts returned by the :meth:`get_cameras` and
        :meth:`get_stem_detectors` methods. The embedded dicts have a key "type" with value "CAMERA" or "STEM_DETECTOR"
        identifying the detector type.

        .. seealso::
            :meth:`get_cameras`, :meth:`get_stem_detectors`

        .. deprecated: 2.0
            Use :meth:`get_stem_detectors` or :meth:`get_cameras` instead.
        """
        import warnings
        warnings.warn("Microscope.get_detectors() is deprecated. Please use get_stem_detectors() or get_cameras() "
                      "instead.", DeprecationWarning)
        result = {}
        result.update(self.get_cameras())
        result.update(self.get_stem_detectors())
        return result

    @abstractmethod
    def get_camera_param(self, name):
        """
        Return dictionary with parameters for camera *name*.

        The returned dictionary has the following keys:

            * "image_size": Size of image (see :class:`AcqImageSize`): "FULL", "HALF", ...
            * "binning": Binning
            * "exposure(s)": Exposure time in seconds
            * "correction": Correction mode (see :class:`AcqImageCorrection`)
            * "exposure_mode": Exposure mode (see :class:`AcqExposureMode`)
            * "shutter_mode": Shutter mode (see :class:`AcqShutterMode`)
            * "pre_exposure(s)": Pre exposure time in seconds
            * "pre_exposure_pause(s)": Pre exposure pause time in seconds

        .. versionadded:: 2.0

        .. note::
            On Titan 1.1 software the "exposure_time(s)" value might not reflect the correct exposure
            time. See :ref:`restrictions`.
        """
        raise NotImplementedError

    @abstractmethod
    def set_camera_param(self, name, values, ignore_errors=False):
        """
        Set parameters for camera *name*. The parameters should be given as a dictionary.
        Allowed keys are described in the :meth:`get_camera_param` method.

        When *ignore_errors* is set and setting of a parameter fails, no error is raised.
        If an unknown camera *name* is used, an error is raised nevertheless.

        :raises KeyError: If an unknown camera *name* is used.

        .. versionadded:: 2.0

        .. note::

            * On Titan 1.1 software setting the "binning" property also changes the exposure time.
            * On Titan 1.1 software images acquired after setting the "exposure_time(s)" property might not be acquired
              with the new setting, even though this property reflects the new value when read.

            Also see :ref:`restrictions`.
        """
        raise NotImplementedError

    @abstractmethod
    def get_stem_detector_param(self, name):
        """
        Return dictionary with parameters for detector *name*.

        The returned dictionary has the following keys:

            * "brightness": Brightness settings
            * "contrast": Contrast setting

        .. versionadded:: 2.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_stem_detector_param(self, name, values, ignore_errors=False):
        """
        Set parameters for STEM detector *name*. The parameters should be given as a dictionary.
        Allowed keys are described in the :meth:`get_stem_detector_param` method.

        When *ignore_errors* is set and setting of a parameter fails, no error is raised.
        If an unknown detector *name* is used, an error is raised nevertheless.

        :raises KeyError: If an unknown detector *name* is used.

        .. versionadded:: 2.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_stem_acquisition_param(self):
        """
        Return dictionary with STEM acquisition parameters.

        The returned dictionary has the following keys:

            * "image_size": Size of image (see :class:`AcqImageSize`): "FULL", "HALF", ...
            * "binning": Binning
            * "dwell_time(s)": Dwell time in seconds

        .. versionadded:: 2.0

        .. note::
            On Titan 1.1 software reading the parameters fails, if STEM is not available. See :ref:`restrictions`.
        """
        raise NotImplementedError

    @abstractmethod
    def set_stem_acquisition_param(self, values, ignore_errors=False):
        """
        Set parameters for STEM acquisition. The parameters should be given as a dictionary.
        Allowed keys are described in the :meth:`get_stem_acquisition_param` method.

        When *ignore_errors* is set and setting of a parameter fails, no error is raised.

        .. versionadded:: 2.0
        """
        raise NotImplementedError

    def get_detector_param(self, name):
        """
        Return parameters for detector `name` as dictionary.

        For "CAMERA" detectors the dict will have the following keys:

            * "image_size": Size of image (see :class:`AcqImageSize`): "FULL", "HALF", ...
            * "binning": Binning
            * "exposure(s)": Exposure time in seconds
            * "correction": Correction mode (see :class:`AcqImageCorrection`)
            * "exposure_mode": Exposure mode (see :class:`AcqExposureMode`)
            * "shutter_mode": Shutter mode (see :class:`AcqShutterMode`)
            * "pre_exposure(s)": Pre exposure time in seconds
            * "pre_exposure_pause(s)": Pre exposure pause time in seconds

        For "STEM_DETECTORS" the dict will have the following keys:

            * "brightness": Brightness settings
            * "contrast": Contrast setting
            * "image_size": Size of image (see :class:`AcqImageSize`): "FULL", "HALF", ...
            * "binning": Binning
            * "dwell_time(s)": Dwell time in seconds

        .. versionchanged:: 2.0
            Key returning dwell time renamed from 'dwelltime(s)' to 'dwell_time(s)'

        .. deprecated:: 2.0
            Use the methods :meth:`get_camera_param`,  :meth:`get_stem_param`, or :meth:`get_stem_acquisition_param`
            instead.
        """
        import warnings
        warnings.warn("Microscope.get_detector_param() is deprecated. Please use get_stem_detector_param() or "
                      "get_camera_param() instead.", DeprecationWarning)
        try:
            param = self.get_camera_param(name)
        except KeyError:
            try:
                param = self.get_stem_detector_param(name)
            except KeyError:
                raise KeyError("No detector with name %s" % name)
            else:
                param.update(self.get_stem_acquisition_param())
        return param

    def set_detector_param(self, name, param):
        """
        Set parameters for detector *name*. The parameters should be given as a dictionary.
        Allowed keys are described in the :meth:`get_detector_param` method.
        If setting a parameter fails, no error is given. Unknown parameters are ignored.

        .. versionchanged:: 2.0
            Dwell time can be set by parameters 'dwelltime(s)' and 'dwell_time(s)'.

        .. deprecated:: 2.0
            Use the methods :meth:`set_camera_param`, :meth:`set_stem_detector_param`,
            or :meth:`set_stem_acquisition_param` instead.
        """
        import warnings
        warnings.warn("Microscope.set_detector_param() is deprecated. Please use set_stem_detector_param(),"
                      "set_camera_param(), or set_stem_acquisition_param() instead.", DeprecationWarning)
        try:
            param = self.set_camera_param(name, param, ignore_errors=True)
        except KeyError:
            try:
                param = self.set_stem_detector_param(name, param, ignore_errors=True)
            except KeyError:
                raise KeyError("No detector with name %s" % name)
            else:
                if ('dwelltime(s)' in param) and not ('dwell_time(s)' in param):
                    param = dict(param)
                    param['dwell_time(s)'] = param.pop('dwelltime(s)')
                self.set_stem_acquisition_param(param, ignore_errors=True)
        return param

    @abstractmethod
    def acquire(self, *args):
        """
        Acquire images for all detectors given as argument.
        The images are returned in an dict indexed by detector name.
        """
        raise NotImplementedError

    @abstractmethod
    def get_image_shift(self):
        """
        Return image shift as (x,y) tuple in meters.

         .. note::
            The accuracy of this value depends on the accuracy of the calibration within the microscope.

        On FEI microscopes this corresponds to the state of "User Image Shift" (in different units though).
        """
        raise NotImplementedError

    @abstractmethod
    def set_image_shift(self, pos):
        """
        Set image shift to position `pos`, which should be an (x, y) tuple, as returned for instance by
        :meth:`get_image_shift`.
        """
        raise NotImplementedError

    @abstractmethod
    def get_beam_shift(self):
        """
        Return beam shift as (x,y) tuple in meters.

        .. note::
            The accuracy of this value depends on the accuracy of the calibration within the microscope.

        On FEI microscopes this corresponds to the state of "User Beam Shift" (in different units though).
        """
        raise NotImplementedError

    @abstractmethod
    def set_beam_shift(self, shift):
        """
        Set beam shift to position `shift`, which should be an (x, y) tuple, as returned for instance by
        :meth:`get_beam_shift`.

        :param shift: Shift value
        :type shift: Tuple[float, float]
        """
        raise NotImplementedError

    @abstractmethod
    def get_beam_tilt(self):
        """
        Return beam tilt as (x, y) tuple.

        The units this is returned in are radians. The accuracy of ths value depends on the accuracy of the
        calibration within the microscope and thus is better not to be trusted blindly.

        On FEI microscopes this corresponds to the state of "DF Tilt", however the tilt is always returned in
        cartesian coordinates.
        """
        raise NotImplementedError

    @abstractmethod
    def set_beam_tilt(self, tilt):
        """
        Set beam tilt to position `tilt`, which should be an (x, y) tuple, as returned for instance by
        :meth:`get_beam_tilt`.

        On FEI microscopes, this will turn on dark field mode, unless (0, 0) is set.
        If (0, 0) is set, dark field mode is turned off.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, mode="ALL"):
        """
        Normalize some or all lenses.

        Possible values for lenses are:

            * "SPOTSIZE": The C1 lens
            * "INTENSITY": The C2 and - if present - the C3 lens
            * "CONDENSER": C1, C2, and - if present - the C3 lens
            * "MINI_CONDENSER": The mini condenser lens
            * "OBJECTIVE": Objective and mini condenser lens
            * "PROJECTOR": Projective lenses (DL, IL, P1, P2)
            * "OBJECTIVE_CONDENSER": Objective and condenser system
            * "OBJECTIVE_PROJECTOR": Objective and projector system
            * "ALL": All lenses

        :param mode: What to normalize. If omitted, all lenses are normalized.
        :type mode: str

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def get_projection_sub_mode(self):
        """
        Return current projection sub mode.

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def get_projection_mode(self):
        """
        Return current projection mode.

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def set_projection_mode(self, mode):
        """
        Set projection mode.

        :param mode: Projection mode: "DIFFRACTION" or "IMAGING"
        :type mode: Literal['DIFFRACTION', 'IMAGING']

        .. versionadded:: 1.0.9

        .. note::
            On Titan 1.1 software changing the mode from IMAGING to DIFFRACTION and back again changes the
            magnification. See :ref:`restrictions`.
        """
        raise NotImplementedError

    @abstractmethod
    def get_projection_mode_string(self):
        """
        Return description of current projection mode. Possible return values are: "LM", Mi", "SA", "Mh", "LAD", and "D"

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def get_magnification_index(self):
        """
        Return index of current magnification/camera length.

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def set_magnification_index(self, index):
        """
        Set magnification / camera length index.

        :param index: Magnification/Camera length index
        :type index: int

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def get_indicated_camera_length(self):
        """
        Return (indicated) camera length in meters in diffraction modes.
        If microscope is in imaging mode, 0 is returned.

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def get_indicated_magnification(self):
        """
        Return (indicated) magnification in imaging modes.
        If microscope is in diffraction mode, 0 is returned.

        .. note::
            On Titan 1.1 software this method returns 0.0 regardless of used mode. See :ref:`restrictions`.

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def get_defocus(self):
        """
        Return defocus value. The returned value is in arbitrary units.
        Increasing values go into overfocus direction, negative values into underfocus direction.

        .. note::
            On Titan 1.1 software the defocus value is the actual defocus relative to the eucentric defocus in meters.
            The accuracy of this value depends on the accuracy of the calibration within the microscope.

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def set_defocus(self, value):
        """
        Set defocus value. The value is in arbitrary units. Increasing values go into overfocus direction, negative
        values into underfocus direction.

        .. note::
            On Titan 1.1 software the defocus value is the actual defocus relative to the eucentric defocus in meters.
            The accuracy of this value depends on the accuracy of the calibration within the microscope.

        :param value: Defocus to set
        :type value: float

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def get_objective_excitation(self):
        """
        Return excitation of objective lens.

        .. versionadded:: 1.0.9
        """
        raise NotImplementedError

    @abstractmethod
    def get_intensity(self):
        """
        Return intensity value.

        The returned value is in arbitrary units.
        Increasing values go into overfocus direction, negative values into underfocus direction.

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def set_intensity(self, value):
        """
        Set intensity.

        The value is in arbitrary units.
        Increasing values go into overfocus direction, negative values into underfocus direction.

        :param value: Intensity to set
        :type value: float

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def get_objective_stigmator(self):
        """
        Return value of objective shift

        :returns: (x, y) tuple with objective shift value

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def set_objective_stigmator(self, value):
        """
        Set objective stigmator.

        :param value: (x, y) tuple, as returned for instance by :meth:`get_objective_stigmator`.

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def get_condenser_stigmator(self):
        """
        Return value of condenser shift

        :returns: (x, y) tuple with condenser shift value

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def set_condenser_stigmator(self, value):
        """
        Set condenser stigmator.

        :param value: (x, y) tuple, as returned for instance by :meth:`get_condenser_stigmator`.

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def get_diffraction_shift(self):
        """
        Return value of diffraction shift

        :returns: (x, y) tuple with diffraction shift value

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def set_diffraction_shift(self, value):
        """
        Set diffraction shift.

        :param value: (x, y) tuple, as returned for instance by :meth:`get_diffraction_shift`.

        .. versionadded:: 1.0.10
        """
        raise NotImplementedError

    @abstractmethod
    def get_screen_current(self):
        """
        Get current on fluorescent screen

        :returns: Screen currrent in Amperes

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_screen_position(self):
        """
        Get position of fluorescent screen

        :rtype: Literal['UP', 'DOWN', 'UNKNOWN']

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_screen_position(self, mode):
        """
        Set position of fluorescent screen

        :type mode: Literal['UP', 'DOWN']

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_illumination_mode(self):
        """
        Get illumination mode (mini condenser setting)

        :rtype: Literal['NANOPROBE', 'MICROPROBE']

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_illumination_mode(self, mode):
        """
        Set illumination mode (mini condenser setting)

        :type mode: Literal['NANOPROBE', 'MICROPROBE']

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_condenser_mode(self):
        """
        Get condenser mode

        :rtype: Literal['PARALLEL', 'PROBE']

        .. note::
            This method is only available on microscopes of the ``TITAN`` family. 

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_condenser_mode(self, mode):
        """
        Set condenser mode

        :type mode: Literal['PARALLEL', 'PROBE']

        .. note::
            This method is only available on microscopes of the ``TITAN`` family. 

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_stem_magnification(self):
        """
        Get STEM magnification

        :rtype: float

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_stem_magnification(self, value):
        """
        Set STEM magnification

        :type value: float

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_stem_rotation(self):
        """
        Get STEM rotation (radian)

        :rtype: float

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_stem_rotation(self, value):
        """
        Set STEM rotation (radian)

        :type value: float

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_illuminated_area(self):
        """
        Return illuminated area. 
        
        TEM scripting manual states the result is in meters, however it is unclear what is
        actually meant (diameter?)
        
        :rtype: float 
        
        .. note::
            This method is only available on microscopes of the ``TITAN`` family.

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_illuminated_area(self, value):
        """
        Set illuminated area.
        
        TEM scripting manual states the result is in meters, however it is unclear what is
        actually meant (diameter?)
        
        :type value: float
        
        .. note::
            This method is only available on microscopes of the ``TITAN`` family.

        ..versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_probe_defocus(self):
        """
        Return probe defocus (meters).

        :rtype: float

        .. note::
            This method is only available on microscopes of the ``TITAN`` family.

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_probe_defocus(self, value):
        """
        Set probe defocus (meters).

        :type value: float

        .. note::
            This method is only available on microscopes of the ``TITAN`` family.

        ..versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_convergence_angle(self):
        """
        Return convergence angle (radian)

        :rtype: float

        .. note::
            This method is only available on microscopes of the ``TITAN`` family.

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_convergence_angle(self, value):
        """
        Set convergence angle (radian).

        :type value: float

        .. note::
            This method is only available on microscopes of the ``TITAN`` family.

        ..versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_spot_size_index(self):
        """
        Get spot size index.

        :rtype: int

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_spot_size_index(self, index):
        """
        Set spot size index.

        :type index: int

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_dark_field_mode(self):
        """
        Get dark field mode.

        .. note::
            :meth:`set_beam_tilt` might change this value.

        :rtype: Literal['OFF', 'CARTESIAN', 'CONICAL]

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_dark_field_mode(self, mode):
        """
        Set dark field mode.

        .. note::
            :meth:`set_beam_tilt` might change this value.

        :type mode: Literal['OFF', 'CARTESIAN', 'CONICAL']

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_beam_blanked(self):
        """
        Return whether the beam is blanked.

        :rtype: bool

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_beam_blanked(self, mode):
        """
        Enable beam blanker

        :type mode: bool

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def is_stem_available(self):
        """
        Return whether the microscope has STEM capabilities.

        :rtype: bool

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_instrument_mode(self):
        """
        Get instrument mode.

        :rtype: Literal['TEM', 'STEM']

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def set_instrument_mode(self, mode):
        """
        Set instrument mode.

        :type mode: Literal['TEM', 'STEM]

        .. versionadded:: 2.0.0
        """
        raise NotImplementedError

    def get_state(self):
        """
        Return a dictionary with state of the microscope.

        .. versionadded:: 1.0.9

        .. versionchanged:: 2.0
            The method was renamed from get_optics_state() to get_state()
        """
        state = {
            "family": self.get_family(),
            "microscope_id": self.get_microscope_id(),
            "temscript_version": self.get_version(),
            "voltage(kV)": self.get_voltage(),
            "stage_holder": self.get_stage_holder(),
            "stage_position": self.get_stage_position(),
            "image_shift": self.get_image_shift(),
            "beam_shift": self.get_beam_shift(),
            "beam_tilt": self.get_beam_tilt(),
            "projection_sub_mode": self.get_projection_sub_mode(),
            "projection_mode": self.get_projection_mode(),
            "projection_mode_string": self.get_projection_mode_string(),
            "magnification_index": self.get_magnification_index(),
            "indicated_camera_length": self.get_indicated_camera_length(),
            "indicated_magnification": self.get_indicated_magnification(),
            "defocus": self.get_defocus(),
            "objective_excitation": self.get_objective_excitation(),
            "intensity": self.get_intensity(),
            "condenser_stigmator": self.get_condenser_stigmator(),
            "objective_stigmator": self.get_objective_stigmator(),
            "diffraction_shift": self.get_diffraction_shift(),
            "screen_current": self.get_screen_current(),
            "screen_position": self.get_screen_position(),
            "spot_size_index": self.get_spot_size_index(),
            "illumination_mode": self.get_illumination_mode(),
            "beam_blanked": self.get_beam_blanked(),
            "stem_available": self.is_stem_available(),
            "instrument_mode": self.get_instrument_mode(),
        }
        if self.get_family() == "TITAN":
            state["condenser_mode"] = self.get_condenser_mode()
            state["illuminated_area"] = self.get_illuminated_area()
            state["convergence_angle"] = self.get_convergence_angle()
            state["probe_defocus"] = self.get_probe_defocus()
        if self.get_instrument_mode() == "STEM":
            state["stem_magnification"] = self.get_stem_magnification()
            state["stem_rotation"] = self.get_stem_rotation()
        return state

    def get_optics_state(self):
        """
        Return a dictionary with state of microscope optics.

        .. versionadded:: 1.0.9

        .. deprecated:: 2.0
            use :meth:`get_state` instead.
        """
        import warnings
        warnings.warn("Microscope.get_optics_state() is deprecated. Use get_state() instead.", DeprecationWarning)
        return self.get_state()
