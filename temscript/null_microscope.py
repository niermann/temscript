from enum import Enum

import numpy as np
from math import pi

from .enums import *
from .base_microscope import BaseMicroscope, parse_enum


def try_update(dest, source, key, cast=None, min_value=None, max_value=None, ignore_errors=False):
    try:
        value = source.pop(key)
    except KeyError:
        return False

    if callable(cast):
        try:
            value = cast(value)
        except (KeyError, ValueError):
            if ignore_errors:
                return False
            raise

    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(max_value, value)

    dest[key] = value
    return True


def try_update_enum(dest, source, key, enum_type, ignore_errors=False):
    try:
        value = source.pop(key)
    except KeyError:
        return False

    try:
        value = parse_enum(enum_type, value)
    except (KeyError, ValueError):
        if ignore_errors:
            return False
        raise

    dest[key] = value
    return True


def unpack_enums(mapping):
    result = {}
    for key, value in mapping.items():
        if isinstance(value, Enum):
            value = value.name
        result[key] = value
    return result


class NullMicroscope(BaseMicroscope):
    """
    Microscope-like class which emulates an microscope.

    :param wait_exposure: Whether the acquire calls waits the exposure time until returning, emulating
        the timing of the real microscope
    :type wait_exposure: bool
    :param voltage: High tension value the microscope report in kV
    :type voltage: float
    """
    STAGE_XY_RANGE = 1e-3       # meters
    STAGE_Z_RANGE = 0.3e-3      # meters
    STAGE_AB_RANGE = pi / 6.0   # radians

    CCD_SIZE = 2048
    CCD_BINNINGS = [1, 2, 4, 8]

    NORMALIZATION_MODES = ("SPOTSIZE", "INTENSITY", "CONDENSER", "MINI_CONDENSER", "OBJECTIVE", "PROJECTOR",
                           "OBJECTIVE_CONDENSER", "OBJECTIVE_PROJECTOR", "ALL")

    def __init__(self, wait_exposure=None, voltage=200.0):
        self._column_valves = False
        self._stage_pos = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'a': 0.0, 'b': 0.0}
        self._wait_exposure = bool(wait_exposure) if wait_exposure is not None else True
        self._ccd_param = {
            "image_size": AcqImageSize.FULL,
            "exposure(s)": 1.0,
            "binning": 1,
            "correction": AcqImageCorrection.DEFAULT,
            "exposure_mode": AcqExposureMode.NONE,
            "shutter_mode": AcqShutterMode.POST_SPECIMEN,
            "pre_exposure(s)": 0.0,
            "pre_exposure_pause(s)": 0.0
        }
        self._stem_acq_param = {
            "image_size": AcqImageSize.FULL,
            "dwell_time(s)": 1e-6,
            "binning": 1,
        }
        self._voltage = voltage
        self._image_shift = np.zeros(2, dtype=float)
        self._beam_shift = np.zeros(2, dtype=float)
        self._beam_tilt = np.zeros(2, dtype=float)
        self._condenser_stigmator = np.zeros(2, dtype=float)
        self._objective_stigmator = np.zeros(2, dtype=float)
        self._diffraction_shift = np.zeros(2, dtype=float)
        self._projection_sub_mode = ProjectionSubMode.SA
        self._projection_mode = ProjectionMode.IMAGING
        self._illumination_mode = IlluminationMode.MICROPROBE
        self._condenser_mode = CondenserMode.PARALLEL
        self._stem_magnification = 100000.0
        self._stem_rotation = 0.0
        self._illuminated_area = 1e-8
        self._probe_defocus = 0.0
        self._convergence_angle = 0.01
        self._spot_size = 1
        self._magnification_index = 10
        self._defocus = 0.0
        self._intensity = 0.0
        self._screen_position = ScreenPosition.DOWN
        self._dark_field_mode = DarkFieldMode.OFF
        self._beam_blanked = False

    def get_family(self):
        return "NULL"

    def get_microscope_id(self):
        import socket
        return socket.gethostname()

    def get_version(self):
        from .version import __version__
        return __version__

    def get_voltage(self):
        return self._voltage

    def get_vacuum(self):
        return {
            "status": VacuumStatus.READY.name,
            "column_valves_open": self._column_valves,
            "pvp_running": False,
            "gauges(Pa)": {},
        }

    def get_stage_holder(self):
        return StageHolderType.SINGLE_TILT.name

    def get_stage_status(self):
        return StageStatus.READY.name

    def get_stage_limits(self):
        return {
            "x": (-self.STAGE_XY_RANGE, +self.STAGE_XY_RANGE),
            "y": (-self.STAGE_XY_RANGE, +self.STAGE_XY_RANGE),
            "z": (-self.STAGE_Z_RANGE, +self.STAGE_Z_RANGE),
            "a": (-self.STAGE_AB_RANGE, +self.STAGE_AB_RANGE),
            "b": (-self.STAGE_AB_RANGE, +self.STAGE_AB_RANGE)
        }

    def get_stage_position(self):
        return dict(self._stage_pos)

    def _set_stage_position(self, pos=None, method="GO", speed=None):
        if method not in ["GO", "MOVE"]:
            raise ValueError("Unknown movement methods.")
        limit = self.get_stage_limits()
        for key in self._stage_pos.keys():
            if key not in pos:
                continue
            mn, mx = limit[key]
            value = max(mn, min(mx, float(pos[key])))
            self._stage_pos[key] = value

    def get_cameras(self):
        return {
            "CCD": {
                "type": "CAMERA",
                "width": self.CCD_SIZE,
                "height": self.CCD_SIZE,
                "pixel_size(um)": 24,
                "binnings": self.CCD_BINNINGS,
                "shutter_modes": ["POST_SPECIMEN"],
                "pre_exposure_limits": (0.0, 0.0),
                "pre_exposure_pause_limits": (0.0, 0.0),
            }
        }

    def get_stem_detectors(self):
        return {}

    def get_camera_param(self, name):
        if name == "CCD":
            return unpack_enums(self._ccd_param)
        else:
            raise KeyError("Unknown detector")

    def set_camera_param(self, name, param, ignore_errors=False):
        # Not implemented: raise error on unknown keys in param
        if name == "CCD":
            param = dict(param)
            try_update_enum(self._ccd_param, param, 'image_size', AcqImageSize, ignore_errors=ignore_errors)
            try_update(self._ccd_param, param, 'exposure(s)', cast=float, min_value=0.0, ignore_errors=ignore_errors)
            try_update(self._ccd_param, param, 'binning', cast=int, min_value=1, ignore_errors=ignore_errors)
            try_update_enum(self._ccd_param, param, 'correction', AcqImageCorrection, ignore_errors=ignore_errors)
        else:
            raise TypeError("Unknown detector.")

    def get_stem_detector_param(self, name):
        raise KeyError("Unknown detector")

    def set_stem_detector_param(self, name, values, ignore_errors=False):
        raise KeyError("Unknown detector")

    def get_stem_acquisition_param(self):
        return unpack_enums(self._stem_acq_param)

    def set_stem_acquisition_param(self, param, ignore_errors=False):
        # Not implemented: raise error on unknown keys in param
        param = dict(param)
        try_update_enum(self._stem_acq_param, param, 'image_size', AcqImageSize, ignore_errors=ignore_errors)
        try_update(self._stem_acq_param, param, 'dwell_time(s)', cast=float, min_value=1e-9,
                   ignore_errors=ignore_errors)
        try_update(self._stem_acq_param, param, 'image_size', cast=int, min_value=1, ignore_errors=ignore_errors)
        if not ignore_errors and param:
            raise ValueError("Unknown keys in parameter dictionary.")

    def acquire(self, *args):
        result = {}
        detectors = set(args)
        for det in detectors:
            if det == "CCD":
                size = self.CCD_SIZE // self._ccd_param["binning"]
                if self._ccd_param["image_size"] == AcqImageSize.HALF:
                    size //= 2
                elif self._ccd_param["image_size"] == AcqImageSize.QUARTER:
                    size //= 4
                if self._wait_exposure:
                    import time
                    time.sleep(self._ccd_param["exposure(s)"])
                result["CCD"] = np.zeros((size, size), dtype=np.int16)
        return result

    def get_image_shift(self):
        return tuple(self._image_shift)

    def set_image_shift(self, pos):
        pos = np.atleast_1d(pos)
        self._image_shift[...] = pos

    def get_beam_shift(self):
        return tuple(self._beam_shift)

    def set_beam_shift(self, pos):
        pos = np.atleast_1d(pos)
        self._beam_shift[...] = pos

    def get_beam_tilt(self):
        return tuple(self._beam_tilt)

    def set_beam_tilt(self, tilt):
        tilt = np.atleast_1d(tilt)
        self._beam_tilt[...] = tilt
        if np.allclose(self._beam_tilt, 0.0):
            self._dark_field_mode = DarkFieldMode.OFF
        elif self._dark_field_mode != DarkFieldMode.OFF:
            self._dark_field_mode = DarkFieldMode.CARTESIAN

    def normalize(self, mode="ALL"):
        if mode.upper() not in NullMicroscope.NORMALIZATION_MODES:
            raise ValueError("Unknown normalization mode: %s" % mode)

    def get_projection_sub_mode(self):
        return self._projection_sub_mode.name

    def get_projection_mode(self):
        return self._projection_mode.name

    def set_projection_mode(self, mode):
        mode = parse_enum(ProjectionMode, mode)
        self._projection_mode = mode

    def get_projection_mode_string(self):
        return "SA"

    def get_magnification_index(self):
        return self._magnification_index

    def set_magnification_index(self, index):
        self._magnification_index = index

    def get_indicated_camera_length(self):
        if self._projection_mode == ProjectionMode.DIFFRACTION:
            return self._magnification_index * 0.1
        else:
            return 0

    def get_indicated_magnification(self):
        if self._projection_mode == ProjectionMode.IMAGING:
            return self._magnification_index * 10000
        else:
            return 0

    def get_defocus(self):
        return self._defocus

    def set_defocus(self, value):
        self._defocus = float(value)

    def get_objective_excitation(self):
        return self._defocus

    def get_intensity(self):
        return self._intensity

    def set_intensity(self, value):
        self._intensity = float(value)

    def get_objective_stigmator(self):
        return tuple(self._objective_stigmator)

    def set_objective_stigmator(self, value):
        value = np.atleast_1d(value)
        self._objective_stigmator[...] = value

    def get_condenser_stigmator(self):
        return tuple(self._condenser_stigmator)

    def set_condenser_stigmator(self, value):
        value = np.atleast_1d(value)
        self._condenser_stigmator[...] = value

    def get_diffraction_shift(self):
        return tuple(self._diffraction_shift)

    def set_diffraction_shift(self, value):
        value = np.atleast_1d(value)
        self._diffraction_shift[...] = value

    def get_screen_current(self):
        return 1e-9

    def get_screen_position(self):
        return self._screen_position.name

    def set_screen_position(self, mode):
        mode = parse_enum(ScreenPosition, mode)
        self._screen_position = mode

    def get_illumination_mode(self):
        return self._illumination_mode.name

    def set_illumination_mode(self, mode):
        mode = parse_enum(IlluminationMode, mode)
        self._illumination_mode = mode

    def get_condenser_mode(self):
        return self._condenser_mode.name

    def set_condenser_mode(self, mode):
        mode = parse_enum(CondenserMode, mode)
        self._condenser_mode = mode

    def get_stem_magnification(self):
        return self._stem_magnification

    def set_stem_magnification(self, value):
        self._stem_magnification = float(value)

    def get_stem_rotation(self):
        return self._stem_rotation

    def set_stem_rotation(self, value):
        self._stem_rotation = float(value)

    def get_illuminated_area(self):
        return self._illuminated_area

    def set_illuminated_area(self, value):
        self._illuminated_area = float(value)

    def get_probe_defocus(self):
        return self._probe_defocus

    def set_probe_defocus(self, value):
        self._probe_defocus = float(value)

    def get_convergence_angle(self):
        return self._convergence_angle

    def set_convergence_angle(self, value):
        self._convergence_angle = float(value)

    def get_spot_size_index(self):
        return self._spot_size

    def set_spot_size_index(self, index):
        self._spot_size = min(max(index, 1), 11)

    def get_dark_field_mode(self):
        return self._dark_field_mode.name

    def set_dark_field_mode(self, mode):
        mode = parse_enum(DarkFieldMode, mode)
        self._dark_field_mode = mode

    def get_beam_blanked(self):
        return self._beam_blanked

    def set_beam_blanked(self, mode):
        self._beam_blanked = bool(mode)

    def is_stem_available(self):
        return False

    def get_instrument_mode(self):
        return InstrumentMode.TEM.name

    def set_instrument_mode(self, mode):
        mode = parse_enum(InstrumentMode, mode)
        if mode != InstrumentMode.TEM:
            raise ValueError("STEM not available.")
