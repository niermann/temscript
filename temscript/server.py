#!/usr/bin/python
import numpy as np
import json
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, quote, unquote
from io import BytesIO

from .base_microscope import STAGE_AXES, parse_enum


# Numpy array encoding JSON encoder
class ArrayJSONEncoder(json.JSONEncoder):
    allowed_dtypes = {"INT8", "INT16", "INT32", "INT64", "UINT8", "UINT16", "UINT32", "UINT64", "FLOAT32", "FLOAT64"}

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            import sys, base64

            dtype_name = obj.dtype.name.upper()
            if dtype_name not in self.allowed_dtypes:
                return json.JSONEncoder.default(self, obj)

            if obj.dtype.byteorder == '<':
                endian = "LITTLE"
            elif obj.dtype.byteorder == '>':
                endian = "BIG"
            else:
                endian = sys.byteorder.upper()

            return {
                'width': obj.shape[1],
                'height': obj.shape[0],
                'type': dtype_name,
                'endianness': endian,
                'encoding': "BASE64",
                'data': base64.b64encode(obj).decode("ascii")
            }
        return json.JSONEncoder.default(self, obj)


def _gzipencode(content):
    """GZIP encode bytes object"""
    import gzip
    out = BytesIO()
    f = gzip.GzipFile(fileobj=out, mode='w', compresslevel=5)
    f.write(content)
    f.close()
    return out.getvalue()


class MicroscopeHandler(BaseHTTPRequestHandler):
    def build_response(self, response):
        if response is None:
            self.send_response(204)
            self.end_headers()
            return
        self.send_response(200)

        # Transport encoding
        accept_type = [x.split(';', 1)[0].strip() for x in self.headers.get("Accept", "").split(",")]
        if "application/python-pickle" in accept_type:
            import pickle
            encoded_response = pickle.dumps(response, protocol=2)
            content_type = "application/python-pickle"
        else:
            encoded_response = ArrayJSONEncoder().encode(response).encode("utf-8")
            content_type = "application/json"

        # Compression?
        accept_encoding = [x.split(';', 1)[0].strip() for x in self.headers.get("Accept-Encoding", "").split(",")]
        if len(encoded_response) > 256 and 'gzip' in accept_encoding:
            encoded_response = _gzipencode(encoded_response)
            self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(encoded_response)
        return

    # Handler for V1 GETs
    def do_GET_V1(self, endpoint, query):
        # Check for known endpoints
        response = None
        if endpoint == "family":
            response = self.server.microscope.get_family()
        elif endpoint == "microscope_id":
            response = self.server.microscope.get_microscope_id()
        elif endpoint == "version":
            response = self.server.microscope.get_version()
        elif endpoint == "voltage":
            response = self.server.microscope.get_voltage()
        elif endpoint == "vacuum":
            response = self.server.microscope.get_vacuum()
        elif endpoint == "stage_holder":
            response = self.server.microscope.get_stage_holder()
        elif endpoint == "stage_status":
            response = self.server.microscope.get_stage_status()
        elif endpoint == "stage_position":
            response = self.server.microscope.get_stage_position()
        elif endpoint == "stage_limits":
            response = self.server.microscope.get_stage_limits()
        elif endpoint == "detectors":
            response = self.server.microscope.get_detectors()
        elif endpoint == "cameras":
            response = self.server.microscope.get_cameras()
        elif endpoint == "stem_detectors":
            response = self.server.microscope.get_stem_detectors()
        elif endpoint == "stem_acquisition_param":
            response = self.server.microscope.get_stem_acquisition_param()
        elif endpoint == "image_shift":
            response = self.server.microscope.get_image_shift()
        elif endpoint == "beam_shift":
            response = self.server.microscope.get_beam_shift()
        elif endpoint == "beam_tilt":
            response = self.server.microscope.get_beam_tilt()
        elif endpoint == "projection_sub_mode":
            response = self.server.microscope.get_projection_sub_mode()
        elif endpoint == "projection_mode":
            response = self.server.microscope.get_projection_mode()
        elif endpoint == "projection_mode_string":
            response = self.server.microscope.get_projection_mode_string()
        elif endpoint == "magnification_index":
            response = self.server.microscope.get_magnification_index()
        elif endpoint == "indicated_camera_length":
            response = self.server.microscope.get_indicated_camera_length()
        elif endpoint == "indicated_magnification":
            response = self.server.microscope.get_indicated_magnification()
        elif endpoint == "defocus":
            response = self.server.microscope.get_defocus()
        elif endpoint == "objective_excitation":
            response = self.server.microscope.get_objective_excitation()
        elif endpoint == "intensity":
            response = self.server.microscope.get_intensity()
        elif endpoint == "objective_stigmator":
            response = self.server.microscope.get_objective_stigmator()
        elif endpoint == "condenser_stigmator":
            response = self.server.microscope.get_condenser_stigmator()
        elif endpoint == "diffraction_shift":
            response = self.server.microscope.get_diffraction_shift()
        elif (endpoint == "optics_state") or (endpoint == "state"):
            response = self.server.microscope.get_state()
        elif endpoint.startswith("detector_param/"):
            try:
                name = unquote(endpoint[15:])
                response = self.server.microscope.get_detector_param(name)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
                return
        elif endpoint.startswith("camera_param/"):
            try:
                name = unquote(endpoint[13:])
                response = self.server.microscope.get_camera_param(name)
            except KeyError:
                self.send_error(404, 'Unknown camera: %s' % self.path)
                return
        elif endpoint.startswith("stem_detector_param/"):
            try:
                name = unquote(endpoint[20:])
                response = self.server.microscope.get_stem_detector_param(name)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
                return
        elif endpoint == "acquire":
            try:
                detectors = query["detectors"]
            except KeyError:
                self.send_error(404, 'No detectors: %s' % self.path)
                return
            response = self.server.microscope.acquire(*detectors)
        else:
            self.send_error(404, 'Unknown endpoint: %s' % self.path)
            return
        self.build_response(response)

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
        if endpoint == "stage_position":
            method = decoded_content.get("method", "GO")
            pos = dict((k, decoded_content[k]) for k in decoded_content.keys() if k in STAGE_AXES)
            try:
                pos['speed'] = decoded_content['speed']
            except KeyError:
                pass
            self.server.microscope.set_stage_position(pos, method=method)
        elif endpoint.startswith("camera_param/"):
            try:
                name = unquote(endpoint[13:])
                response = self.server.microscope.set_camera_param(name, decoded_content)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
                return
        elif endpoint.startswith("stem_detector_param/"):
            try:
                name = unquote(endpoint[20:])
                response = self.server.microscope.set_stem_detector_param(name, decoded_content)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
                return
        elif endpoint == "stem_acquisition_param":
            self.server.microscope.set_stem_acquisition_param(decoded_content)
        elif endpoint.startswith("detector_param/"):
            try:
                name = unquote(endpoint[15:])
                response = self.server.microscope.set_detector_param(name, decoded_content)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
                return
        elif endpoint == "image_shift":
            self.server.microscope.set_image_shift(decoded_content)
        elif endpoint == "beam_shift":
            self.server.microscope.set_beam_shift(decoded_content)
        elif endpoint == "beam_tilt":
            self.server.microscope.set_beam_tilt(decoded_content)
        elif endpoint == "projection_mode":
            self.server.microscope.set_projection_mode(decoded_content)
        elif endpoint == "magnification_index":
            self.server.microscope.set_magnification_index(decoded_content)
        elif endpoint == "defocus":
            self.server.microscope.set_defocus(decoded_content)
        elif endpoint == "intensity":
            self.server.microscope.set_intensity(decoded_content)
        elif endpoint == "diffraction_shift":
            self.server.microscope.set_diffraction_shift(decoded_content)
        elif endpoint == "objective_stigmator":
            self.server.microscope.set_objective_stigmator(decoded_content)
        elif endpoint == "condenser_stigmator":
            self.server.microscope.set_condenser_stigmator(decoded_content)
        elif endpoint == "normalize":
            mode = decoded_content
            try:
                self.server.microscope.normalize(mode)
            except ValueError:
                self.send_error(404, 'Unknown mode.' % mode)
                return
        else:
            self.send_error(404, 'Unknown endpoint: %s' % self.path)
            return
        self.build_response(response)

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


class MicroscopeServer(HTTPServer, object):
    def __init__(self, server_address=('', 8080), microscope_factory=None):
        """
        Run a microscope server.

        :param server_address: (address, port) tuple
        :param microscope_factory: callable creating the BaseMicroscope instance to use
        """
        if microscope_factory is None:
            from .microscope import Microscope
            microscope_factory = Microscope
        self.microscope = microscope_factory()
        super(MicroscopeServer, self).__init__(server_address, MicroscopeHandler)
