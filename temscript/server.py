#!/usr/bin/python
from __future__ import division, print_function
import json
import traceback

# Get imports from library
try:
    # Python 3.X
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs, quote
    from io import BytesIO
except ImportError:
    # Python 2.X
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import urlparse, parse_qs, quote
    from cStringIO import StringIO as BytesIO

import temscript.instrument as instrument
from temscript.enums import *


_test = "empty string"


def _gzipencode(self, content):
    """GZIP encode bytes object"""
    import gzip
    out = BytesIO()
    f = gzip.GzipFile(fileobj=out, mode='w', compresslevel=5)
    f.write(content)
    f.close()
    return out.getvalue()


def _parse_enum(type, item):
    """Try to parse 'item' (string or integer) to enum 'type'"""
    try:
        return type[item]
    except:
        return type(item)


class TemscriptHandler(BaseHTTPRequestHandler):
    def send_array_dict(self, data, format):
        if format.startswith("PYTHON_PICKLE_V"):
            import pickle
            protocol = int(format[15:])
            content = pickle.dumps(data, protocol=protocol)
            self.send_response(200)
            self.send_header('Content-type', "application/python-pickle")
        elif format == "BASE64":
            import sys, base64
            response = {}
            for name, array in data.items():
                if array.dtype == '<':
                    endian = "LITTLE"
                elif array.dtype == '>':
                    endian = "BIG"
                else:
                    endian = sys.byteorder.upper()
                response[name] = {
                    'width': array.shape[1],
                    'height': array.shape[0],
                    'type': array.dtype.name,
                    'endianness': endian,
                    'encoding': "BASE64",
                    'data': base64.b64encode(array)
                }
            content = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-type', "application/json")
        else:
            self.send_error(404, 'Unknown format: %s' % self.path)
            return
        # Compress?
        if len(content) > 256 and 'accept-encoding' in self.headers and 'gzip' in self.headers['accept-encoding']:
            content = _gzipencode(content)
            self.send_header('content-encoding', 'gzip')
        self.end_headers()
        self.wfile.write(content)

    # Handler for V1 GETs
    def do_GET_V1(self, endpoint, query):
        # Check for known endpoints
        response = None
        if endpoint == "vacuum":
            response = self.server.tem_get_vacuum()
        elif endpoint == "detectors":
            response = self.server.tem_get_detectors()
        elif endpoint.startswith("detector_param/"):
            try:
                name = endpoint[15:]
                response = self.server.tem_get_detector_param(name)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
                return
        elif endpoint == "acquire":
            try:
                detectors = query["detectors"]
            except KeyError:
                self.send_error(404, 'No detectors: %s' % self.path)
                return
            return_format = query.get("format", ["BASE64"])[0]
            result = self.server.tem_acquire(detectors)
            self.send_array_dict(result, return_format)
            return
        elif endpoint == "test":
            response = _test
        else:
            self.send_error(404, 'Unknown endpoint: %s' % self.path)
            return

        if response is None:
            self.send_response(204)
            self.end_headers()
        else:
            encoded_response = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-type', "application/json")
            self.end_headers()
            self.wfile.write(encoded_response)
        return

    # Handler for V1 PUTs
    def do_PUT_V1(self, endpoint, query):
        # Read content
        length = int(self.headers['Content-Length'])
        if length > 4096:
            raise ValueError("Too much content...")
        content = self.rfile.read(length)
        decoded_content = json.loads(content.decode("utf-8"))

        # Check for known endpoints
        response = None
        if endpoint.startswith("detector_param/"):
            try:
                name = endpoint[15:]
                response = self.server.tem_set_detector_param(name, decoded_content)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
                return
        elif endpoint == "test":
            global _test
            _test = decoded_content
        else:
            self.send_error(404, 'Unknown endpoint: %s' % self.path)
            return

        if response is None:
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-type', "application/json")
            self.end_headers()
            self.wfile.write(response)
        return

    # Handler for the GET requests
    def do_GET(self):
        try:
            request = urlparse(self.path)
            if request.path.startswith("/v1/"):
                self.do_GET_V1(request.path[4:], parse_qs(request.query))
            else:
                self.send_error(404, 'Unknown API version: %s' % self.path)
            return
        except Exception as exc:
            self.log_error("Exception raised during handling of GET request: %s\n%s",
                           self.path, traceback.format_exc())
            self.send_error(500, "Error handling request: %s" % self.path)

    # Handler for the PUT requests
    def do_PUT(self):
        try:
            request = urlparse(self.path)
            if request.path.startswith("/v1/"):
                self.do_PUT_V1(request.path[4:], parse_qs(request.query))
            else:
                self.send_error(404, 'Unknown API version: %s' % self.path)
            return
        except Exception as exc:
            self.log_error("Exception raised during handling of PUT request: %s\n%s",
                           self.path, traceback.format_exc())
            self.send_error(500, "Error handling request: %s" % self.path)

class TemscriptServer(HTTPServer):
    def __init__(self, *args, **kw):
        #self._setup_tem()
        super(TemscriptServer, self).__init__(*args, **kw)

    def _setup_tem(self):
        """Get Instrument interface and subinterfaces"""
        tem = instrument.GetInstrument()
        self._tem_instrument = tem
        self._tem_illumination = tem.Illumination
        self._tem_projection = tem.Projection
        self._tem_stage = tem.Stage
        self._tem_acquisition = tem.Acquisition
        self._tem_vacuum = tem.Vacuum

    def tem_get_vacuum(self):
        gauges = {}
        for g in self._tem_vacuum.Gauges:
            g.Read()
            status = GaugeStatus(g.Status)
            if status == GaugeStatus.UNDERFLOW:
                gauges[g.Name] = "underflow"
            elif status == GaugeStatus.OVERFLOW:
                gauges[g.Name] = "overflow"
            elif status == GaugeStatus.VALID:
                gauges[g.Name] = g.Pressure
        return {
            "status" : VacuumStatus(self._tem_vacuum.Status).name,
            "column_valves_open" : self._tem_vacuum.ColumnValvesOpen,
            "pvp_running" : self._tem_vacuum.PVPRunning,
            "gauges_Pa" : gauges,
        }

    def tem_get_detectors(self):
        detectors = {}
        for cam in self._tem_acquisition.Cameras:
            info = cam.Info
            param = cam.AcqParams
            name = quote(info.Name)
            detectors[name] = {
                "type": DetectorType.CAMERA,
                "height": info.Height,
                "width": info.Width,
                "pixel_size_um": info.PixelSize / 1e-6,
                "binnings": [int(b) for b in info.Binnings],
                "shutter_modes": [AcqShutterMode(x).name for x in info.ShutterModes],
                "min_pre_exposure_s": param.MinPreExposureTime,
                "max_pre_exposure_s": param.MaxPreExposureTime,
                "min_pre_exposure_pause_s": param.MinPreExposurePauseTime,
                "max_pre_exposure_pause_s": param.MaxPreExposurePauseTime
            }
        for stem in self._tem_acquisition.Detectors:
            info = stem.Info
            detectors[name] = {
                "type": DetectorType.STEM_DETECTOR,
                "binnings": [int(b) for b in info.Binnings],
            }
        return detectors

    def _tem_find_detector(self, name):
        for cam in self._tem_acquisition.Cameras:
            if quote(cam.Info.Name) == name:
                return cam
        for stem in self._tem_acquisition.Detectors:
            if quote(stem.Info.Name) == name:
                return stem
        raise KeyError("No detector with name %s" % name)

    def _tem_get_camera_param(self, det):
        info = det.Info
        param = det.AcqParams
        return {
            "image_size": AcqImageSize(param.ImageSize).name,
            "exposure_s": param.ExposureTime,
            "binning": param.Binning,
            "correction": AcqImageCorrection(param.ImageCorrection).name,
            "mode": AcqExposureMode(param.ExposureMode).name,
            "shutter": AcqShutterMode(info.ShutterMode).name,
            "pre_exposure_s": param.PreExposureTime,
            "pre_exposure_pause_s": param.PreExposurePauseTime
        }

    def _tem_set_camera_param(self, det, values):
        info = det.Info
        param = det.AcqParams
        # Silently ignore failures
        try:
            param.ImageSize = _parse_enum(AcqImageSize, values["image_size"])
        except Exception:
            pass
        try:
            param.ExposureTime = values["exposure_s"]
        except Exception:
            pass
        try:
            param.Binning = values["binning"]
        except Exception:
            pass
        try:
            param.ImageCorrection = _parse_enum(AcqImageCorrection, values["correction"])
        except Exception:
            pass
        try:
            param.ExposureMode = _parse_enum(AcqExposureMode, values["exposure"])
        except Exception:
            pass
        try:
            info.ShutterMode = _parse_enum(AcqShutterMode, values["shutter"])
        except Exception:
            pass
        try:
            param.PreExposureTime = values["pre_exposure_s"]
        except Exception:
            pass
        try:
            param.PreExposurePauseTime = values["pre_exposure_pause_s"]
        except Exception:
            pass

    def _tem_get_stem_detector_param(self, det):
        info = det.Info
        param = det.AcqParams
        return {
            "brightness": info.Brightness,
            "contrast": info.Contrast,
            "image_size": AcqImageSize(param.ImageSize).name,
            "binning": param.Binning,
            "dwelltime_s": param.DwellTime
        }

    def _tem_set_stem_detector_param(self, det, values):
        info = det.Info
        param = det.AcqParams
        # Silently ignore failures
        try:
            info.Brightness = values["brightness"]
        except Exception:
            pass
        try:
            info.Contrast = values["contrast"]
        except Exception:
            pass
        try:
            param.ImageSize = _parse_enum(AcqImageSize, values["image_size"])
        except Exception:
            pass
        try:
            param.Binning = values["binning"]
        except Exception:
            pass
        try:
            param.DwellTime = values["dwelltime_s"]
        except Exception:
            pass

    def tem_get_detector_param(self, name):
        det = self._tem_find_detector(name)
        if isinstance(det, instrument.CCDCamera):
            return self._tem_get_camera_param(det)
        elif isinstance(det, instrument.STEMDetector):
            return self._tem_get_stem_detector_param(det)
        else:
            raise TypeError("Unknown detector type.")

    def tem_set_detector_param(self, name, values):
        det = self._tem_find_detector(name)
        if isinstance(det, instrument.CCDCamera):
            self._tem_set_camera_param(det, values)
        elif isinstance(det, instrument.STEMDetector):
            self._tem_set_stem_detector_param(det, values)
        else:
            raise TypeError("Unknown detector type.")

    def tem_acquire(self, detectors):
        self._tem_acquisition.RemoveAllAcqDevices()
        for det in detectors:
            try:
                self._tem_acquisition.AddAcqDeviceByName(det)
            except Exception:
                pass
        # Read as dict of numpy arrays
        images = self._tem_acquisition.AcquireImages()
        result = {}
        for img in images:
            result[quote(img.Name)] = img.Array
        return result

if __name__ == '__main__':
    SERVER_PORT = 8080
    SERVER_HOST = ''    # Empty is any interface

    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = TemscriptServer((SERVER_HOST, SERVER_PORT), TemscriptHandler)
        print("Started httpserver on host '%s' port %d." % (SERVER_HOST, SERVER_PORT))
        print("Press Ctrl+C to stop server.")

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('Ctrl+C received, shutting down the web server')
        server.socket.close()
