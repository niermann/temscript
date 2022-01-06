import math

from temscript.base_microscope import set_enum_attr_from_dict, set_attr_from_dict

from .base_microscope import BaseMicroscope, parse_enum, STAGE_AXES
from .instrument import CCDCamera, GetInstrument, STEMDetector
from .enums import *


class Microscope(BaseMicroscope):
    """
    Hich level interface to local microscope.

    Creating an instance of this class, already queries the COM interface for the instrument.

    Usage:

        >>> microscope = Microscope()
        >>> microscope.get_family()
        "TITAN"
    """
    def __init__(self):
        tem = GetInstrument()
        self._tem_instrument = tem
        self._tem_gun = tem.Gun
        self._tem_illumination = tem.Illumination
        self._tem_projection = tem.Projection
        self._tem_stage = tem.Stage
        self._tem_acquisition = tem.Acquisition
        self._tem_vacuum = tem.Vacuum
        self._tem_camera = tem.Camera
        self._tem_control = tem.InstrumentModeControl
        self._family = tem.Configuration.ProductFamily

    def get_family(self):
        return ProductFamily(self._family).name

    def get_microscope_id(self):
        import socket
        return socket.gethostname()

    def get_version(self):
        from .version import __version__
        return __version__

    def get_voltage(self):
        state = self._tem_gun.HTState
        if state == HighTensionState.ON:
            return self._tem_gun.HTValue * 1e-3
        else:
            return 0.0

    def get_vacuum(self):
        gauges = {}
        for g in self._tem_vacuum.Gauges:
            g.Read()
            status = GaugeStatus(g.Status)
            name = g.Name
            if status == GaugeStatus.UNDERFLOW:
                gauges[name] = "UNDERFLOW"
            elif status == GaugeStatus.OVERFLOW:
                gauges[name] = "OVERFLOW"
            elif status == GaugeStatus.VALID:
                gauges[name] = g.Pressure
        return {
            "status": VacuumStatus(self._tem_vacuum.Status).name,
            "column_valves_open": self._tem_vacuum.ColumnValvesOpen,
            "pvp_running": self._tem_vacuum.PVPRunning,
            "gauges(Pa)": gauges,
        }

    def get_stage_holder(self):
        return self._tem_stage.Holder.name

    def get_stage_status(self):
        return self._tem_stage.Status.name

    def get_stage_limits(self):
        result = {}
        for axis in STAGE_AXES:
            mn, mx, unit = self._tem_stage.AxisData(axis)
            result[axis] = (mn, mx)
        return result

    def get_stage_position(self):
        return self._tem_stage.Position

    def _set_stage_position(self, pos=None, method="GO", speed=None):
        if method == "GO":
            self._tem_stage.GoTo(speed=speed, **pos)
        elif method == "MOVE":
            self._tem_stage.MoveTo(**pos)
        else:
            raise ValueError("Unknown movement method.")

    def get_cameras(self):
        cameras = {}
        for cam in self._tem_acquisition.Cameras:
            info = cam.Info
            param = cam.AcqParams
            name = info.Name
            cameras[name] = {
                "type": "CAMERA",
                "height": info.Height,
                "width": info.Width,
                "pixel_size(um)": tuple(size / 1e-6 for size in info.PixelSize),
                "binnings": [int(b) for b in info.Binnings],
                "shutter_modes": [AcqShutterMode(x).name for x in info.ShutterModes],
                "pre_exposure_limits(s)": (param.MinPreExposureTime, param.MaxPreExposureTime),
                "pre_exposure_pause_limits(s)": (param.MinPreExposurePauseTime, param.MaxPreExposurePauseTime)
            }
        return cameras

    def get_stem_detectors(self):
        detectors = {}
        for stem in self._tem_acquisition.Detectors:
            info = stem.Info
            name = info.Name
            detectors[name] = {
                "type": "STEM_DETECTOR",
                "binnings": [int(b) for b in info.Binnings],
            }
        return detectors

    def _find_camera(self, name):
        """Find camera object by name"""
        if isinstance(name, CCDCamera):
            return name
        for cam in self._tem_acquisition.Cameras:
            if cam.Info.Name == name:
                return cam
        raise KeyError("No camera with name %s" % name)

    def _find_stem_detector(self, name):
        """Find STEM detector object by name"""
        if isinstance(name, STEMDetector):
            return name
        for stem in self._tem_acquisition.Detectors:
            if stem.Info.Name == name:
                return stem
        raise KeyError("No STEM detector with name %s" % name)

    def get_camera_param(self, name):
        camera = self._find_camera(name)
        info = camera.Info
        param = camera.AcqParams
        return {
            "image_size": param.ImageSize.name,
            "exposure(s)": param.ExposureTime,
            "binning": param.Binning,
            "correction": param.ImageCorrection.name,
            "exposure_mode": param.ExposureMode.name,
            "shutter_mode": info.ShutterMode.name,
            "pre_exposure(s)": param.PreExposureTime,
            "pre_exposure_pause(s)": param.PreExposurePauseTime
        }

    def set_camera_param(self, name, values, ignore_errors=False):
        camera = self._find_camera(name)
        values = dict(values)
        info = camera.Info
        param = camera.AcqParams
        set_enum_attr_from_dict(param, 'ImageSize', AcqImageSize, values, 'image_size', ignore_errors=ignore_errors)
        set_attr_from_dict(param, 'Binning', values, 'binning', ignore_errors=ignore_errors)
        set_enum_attr_from_dict(param, 'ImageCorrection', AcqImageCorrection, values, 'correction',
                                ignore_errors=ignore_errors)
        set_enum_attr_from_dict(param, 'ExposureMode', AcqExposureMode, values, 'exposure_mode',
                                ignore_errors=ignore_errors)
        set_enum_attr_from_dict(info, 'ShutterMode', AcqShutterMode, values, 'shutter_mode',
                                ignore_errors=ignore_errors)
        set_attr_from_dict(param, 'PreExposureTime', values, 'pre_exposure(s)', ignore_errors=ignore_errors)
        set_attr_from_dict(param, 'PreExposurePauseTime', values, 'pre_exposure_pause(s)', ignore_errors=ignore_errors)

        # Set exposure after binning, since it adjusted automatically when binning is set
        set_attr_from_dict(param, 'ExposureTime', values, 'exposure(s)', ignore_errors=ignore_errors)

        if not ignore_errors and values:
            raise ValueError("Unknown keys in parameter dictionary.")

    def get_stem_detector_param(self, name):
        det = self._find_stem_detector(name)
        info = det.Info
        return {
            "brightness": info.Brightness,
            "contrast": info.Contrast
        }

    def set_stem_detector_param(self, name, values, ignore_errors=False):
        det = self._find_stem_detector(name)
        values = dict(values)
        info = det.Info
        set_attr_from_dict(info, 'Brightness', values, 'brightness')
        set_attr_from_dict(info, 'Contrast', values, 'contrast')

        if not ignore_errors and values:
            raise ValueError("Unknown keys in parameter dictionary.")

    def get_stem_acquisition_param(self):
        param = self._tem_acquisition.StemAcqParams
        return {
            "image_size": param.ImageSize.name,
            "binning": param.Binning,
            "dwell_time(s)": param.DwellTime
        }

    def set_stem_acquisition_param(self, values, ignore_errors=False):
        values = dict(values)
        param = self._tem_acquisition.StemAcqParams
        set_enum_attr_from_dict(param, 'ImageSize', AcqImageSize, values, 'image_size', ignore_errors=ignore_errors)
        set_attr_from_dict(param, 'Binning', values, 'binning', ignore_errors=ignore_errors)
        set_attr_from_dict(param, 'DwellTime', values, 'dwell_time(s)', ignore_errors=ignore_errors)

        if not ignore_errors and values:
            raise ValueError("Unknown keys in parameter dictionary.")

    def acquire(self, *args):
        self._tem_acquisition.RemoveAllAcqDevices()
        for det in args:
            try:
                self._tem_acquisition.AddAcqDeviceByName(det)
            except Exception:
                pass
        images = self._tem_acquisition.AcquireImages()
        result = {}
        for img in images:
            result[img.Name] = img.Array
        return result

    def get_image_shift(self):
        return self._tem_projection.ImageShift

    def set_image_shift(self, pos):
        self._tem_projection.ImageShift = pos

    def get_beam_shift(self):
        return self._tem_illumination.Shift

    def set_beam_shift(self, pos):
        self._tem_illumination.Shift = pos

    def get_beam_tilt(self):
        mode = self._tem_illumination.DFMode
        tilt = self._tem_illumination.Tilt
        if mode == DarkFieldMode.CONICAL:
            return tilt[0] * math.cos(tilt[1]), tilt[0] * math.sin(tilt[1])
        elif mode == DarkFieldMode.CARTESIAN:
            return tilt
        else:
            return 0.0, 0.0     # Microscope might return nonsense if DFMode is OFF
            
    def set_beam_tilt(self, tilt):
        mode = self._tem_illumination.DFMode
        if tilt[0] == 0.0 and tilt[1] == 0.0:
            self._tem_illumination.Tilt = 0.0, 0.0
            self._tem_illumination.DFMode = DarkFieldMode.OFF
        elif mode == DarkFieldMode.CONICAL:
            self._tem_illumination.Tilt = math.sqrt(tilt[0]**2 + tilt[1]**2), math.atan2(tilt[1], tilt[0])
        elif mode == DarkFieldMode.OFF:
            self._tem_illumination.DFMode = DarkFieldMode.CARTESIAN
            self._tem_illumination.Tilt = tilt
        else:
            self._tem_illumination.Tilt = tilt

    def normalize(self, mode="ALL"):
        mode = mode.upper()
        if mode == "ALL":
            self._tem_instrument.NormalizeAll()
        elif mode == "OBJECTIVE_CONDENSER":
            self._tem_illumination.Normalize(IlluminationNormalization.ALL)
        elif mode == "OBJECTIVE_PROJECTIVE":
            self._tem_projection.Normalize(ProjectionNormalization.ALL)
        else:
            try:
                illum_norm = IlluminationNormalization[mode]
            except KeyError:
                try:
                    proj_norm = ProjectionNormalization[mode]
                except KeyError:
                    raise ValueError("Unknown normalization mode: %s" % mode)
                else:
                    self._tem_projection.Normalize(proj_norm)
            else:
                self._tem_illumination.Normalize(illum_norm)

    def get_projection_sub_mode(self):
        return self._tem_projection.SubMode.name

    def get_projection_mode(self):
        return self._tem_projection.Mode.name

    def set_projection_mode(self, mode):
        mode = parse_enum(ProjectionMode, mode)
        self._tem_projection.Mode = mode

    def get_projection_mode_string(self):
        return ProjectionSubMode(self._tem_projection.SubMode).name

    def get_magnification_index(self):
        return self._tem_projection.ProjectionIndex

    def set_magnification_index(self, index):
        index = int(index)
        self._tem_projection.ProjectionIndex = index

    def get_indicated_camera_length(self):
        return self._tem_projection.CameraLength

    def get_indicated_magnification(self):
        return self._tem_projection.Magnification

    def get_defocus(self):
        return self._tem_projection.Focus

    def set_defocus(self, value):
        self._tem_projection.Focus = float(value)

    def get_objective_excitation(self):
        return self._tem_projection.ObjectiveExcitation

    def get_intensity(self):
        return self._tem_illumination.Intensity

    def set_intensity(self, value):
        self._tem_illumination.Intensity = float(value)

    def get_objective_stigmator(self):
        return self._tem_projection.ObjectiveStigmator

    def set_objective_stigmator(self, value):
        self._tem_projection.ObjectiveStigmator = value

    def get_condenser_stigmator(self):
        return self._tem_illumination.CondenserStigmator

    def set_condenser_stigmator(self, value):
        self._tem_illumination.CondenserStigmator = value

    def get_diffraction_shift(self):
        return self._tem_projection.DiffractionShift

    def set_diffraction_shift(self, value):
        self._tem_projection.DiffractionShift = value

    def get_screen_current(self):
        return self._tem_camera.ScreenCurrent

    def get_screen_position(self):
        return self._tem_camera.MainScreen.name

    def set_screen_position(self, mode):
        mode = parse_enum(ScreenPosition, mode)
        self._tem_camera.MainScreen = mode

    def get_illumination_mode(self):
        return self._tem_illumination.Mode.name

    def set_illumination_mode(self, mode):
        mode = parse_enum(IlluminationMode, mode)
        self._tem_illumination.Mode = mode

    def get_condenser_mode(self):
        return self._tem_illumination.CondenserMode.name

    def set_condenser_mode(self, mode):
        mode = parse_enum(CondenserMode, mode)
        self._tem_illumination.CondenserMode = mode

    def get_stem_magnification(self):
        return self._tem_illumination.StemMagnification

    def set_stem_magnification(self, value):
        self._tem_illumination.StemMagnification = value

    def get_stem_rotation(self):
        return self._tem_illumination.StemRotation

    def set_stem_rotation(self, value):
        self._tem_illumination.StemRotation = value

    def get_illuminated_area(self):
        return self._tem_illumination.IlluminatedArea

    def set_illuminated_area(self, value):
        self._tem_illumination.IlluminatedArea = value

    def get_probe_defocus(self):
        return self._tem_illumination.ProbeDefocus

    def set_probe_defocus(self, value):
        self._tem_illumination.ProbeDefocus = value

    def get_convergence_angle(self):
        return self._tem_illumination.ConvergenceAngle

    def set_convergence_angle(self, value):
        self._tem_illumination.ConvergenceAngle = value

    def get_spot_size_index(self):
        return self._tem_illumination.SpotSizeIndex

    def set_spot_size_index(self, index):
        self._tem_illumination.SpotSizeIndex = index

    def get_dark_field_mode(self):
        return self._tem_illumination.DarkFieldMode.name

    def set_dark_field_mode(self, mode):
        mode = parse_enum(DarkFieldMode, mode)
        self._tem_illumination.DarkFieldMode = mode

    def get_beam_blanked(self):
        return self._tem_illumination.BeamBlanked

    def set_beam_blanked(self, mode):
        self._tem_illumination.BeamBlanked = mode

    def is_stem_available(self):
        return self._tem_control.StemAvailable

    def get_instrument_mode(self):
        return self._tem_control.InstrumentMode.name

    def set_instrument_mode(self, mode):
        mode = parse_enum(InstrumentMode, mode)
        self._tem_control.InstrumentMode = mode
