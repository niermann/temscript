from __future__ import division, print_function
import numpy as np
from math import pi

from .enums import *
from .microscope import _parse_enum


class NullMicroscope(object):
    """
    Microscope-like class which emulates an microscope.

    :param wait_exposure: Whether the acquire calls waits the exposure time until returning, emulating the timing of the real microscope
    :type wait_exposure: bool
    :param voltage: High tension value the microscope report in kV
    :type voltage: float
    """
    STAGE_XY_RANGE = 1e-3       # meters
    STAGE_Z_RANGE = 0.3e-3      # meters
    STAGE_AB_RANGE = pi / 6.0   # radians

    CCD_SIZE = 2048
    CCD_BINNINGS = [1, 2, 4, 8]

    def __init__(self, wait_exposure=None, voltage=200.0):
        self._column_valves = False
        self._stage_pos = { 'x': 0.0, 'y': 0.0, 'z': 0.0, 'a': 0.0, 'b': 0.0 }
        self._wait_exposure = bool(wait_exposure) if wait_exposure is not None else True
        self._ccd_param = {
            "image_size": "FULL",
            "exposure(s)": 1.0,
            "binning": 1,
            "correction": "DEFAULT",
            "exposure_mode": "NONE",
            "shutter_mode": "POST_SPECIMEN",
            "pre_exposure(s)": 0.0,
            "pre_exposure_pause(s)": 0.0
        }
        self._voltage = voltage
        self._image_shift = np.zeros(2, dtype=float)
        self._beam_shift = np.zeros(2, dtype=float)
        self._beam_tilt = np.zeros(2, dtype=float)
        self._projection_mode = ProjectionMode.IMAGING
        self._magnification_index = 10
        self._defocus = 0.0

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
            "status": "READY",
            "column_valves_open": self._column_valves,
            "pvp_running": False,
            "gauges(Pa)": {},
        }

    def get_stage_holder(self):
        return "UNKNOWN"

    def get_stage_status(self):
        return "READY"

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

    def set_stage_position(self, pos, method="GO"):
        if method not in ["GO", "MOVE"]:
            raise ValueError("Unknown movement methods.")
        limit = self.get_stage_limits()
        for key in self._stage_pos.keys():
            if key not in pos:
                continue
            mn, mx = limit[key]
            value = max(mn, min(mx, float(pos[key])))
            self._stage_pos[key] = value

    def get_detectors(self):
        return {
            "CCD" : {
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

    def get_detector_param(self, name):
        if name == "CCD":
            return dict(self._ccd_param)
        else:
            raise ValueError("Unknown detector")

    def set_detector_param(self, name, param):
        if name == "CCD":
            try:
                self._ccd_param["image_size"] = _parse_enum(AcqImageSize, param["image_size"]).name
            except Exception:
                pass
            try:
                self._ccd_param["exposure(s)"] = max(0.0, float(param["exposure(s)"]))
            except Exception:
                pass
            try:
                binning = int(param["exposure(s)"])
                if binning in self.CCD_BINNINGS:
                    self._ccd_param["binning"] = binning
            except Exception:
                pass
            try:
                self._ccd_param["correction"] = _parse_enum(AcqImageCorrection, param["correction"]).name
            except Exception:
                pass
        else:
            raise TypeError("Unknown detector type.")

    def acquire(self, *args):
        result = {}
        detectors = set(args)
        for det in detectors:
            if det == "CCD":
                size = self.CCD_SIZE // self._ccd_param["binning"]
                if self._ccd_param["image_size"] == "HALF":
                    size //= 2
                elif self._ccd_param["image_size"] == "QUARTER":
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

    def normalize(self, mode="ALL"):
        KNOWN_MODES = ["SPOTSIZE", "INTENSITY", "CONDENSER", "MINI_CONDENSER", "OBJECTIVE", "PROJECTOR",
                       "OBJECTIVE_CONDENSER", "OBJECTIVE_PROJECTOR", "ALL"]
        if mode.upper() not in KNOWN_MODES:
            raise ValueError("Unknown normalization mode: %s" % mode)

    def get_projection_mode(self):
        return ProjectionMode(self._projection_mode)

    def set_projection_mode(self, mode):
        mode = _parse_enum(ProjectionMode, mode)
        self._projection_mode = mode

    def get_projection_mode_string(self):
        return "SA"

    def get_magnification_index(self):
        return self._magnification_index

    def set_magnification_index(self, index):
        self.get_magnification_index = index

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

    def get_optics_state(self):
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
            "projection_mode": self.get_projection_mode(),
            "projection_mode_string": self.get_projection_mode_string(),
            "magnification_index": self.get_magnification_index(),
            "indicated_camera_length": self.get_indicated_camera_length(),
            "indicated_magnification": self.get_indicated_magnification(),
            "defocus": self.get_defocus(),
            "objective_excitation": self.get_objective_excitation()
        }
        return state
