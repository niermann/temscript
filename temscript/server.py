#!/usr/bin/python
import numpy as np
import json
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, quote, unquote
from io import BytesIO

from .base_microscope import STAGE_AXES, parse_enum
from .remote_microscope import RequestJsonEncoder

# Numpy array encoding JSON encoder
class ArrayJSONEncoder(RequestJsonEncoder):
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


def gzip_encode(content):
    """GZIP encode bytes object"""
    import gzip
    out = BytesIO()
    f = gzip.GzipFile(fileobj=out, mode='w', compresslevel=5)
    f.write(content)
    f.close()
    return out.getvalue()


class MicroscopeHandler(BaseHTTPRequestHandler):
    GET_V1_FORWARD = ("family", "microscope_id", "version", "voltage", "vacuum", "stage_holder",
                      "stage_status", "stage_position", "stage_limits", "detectors", "cameras", "stem_detectors",
                      "stem_acquisition_param", "image_shift", "beam_shift", "beam_tilt", "projection_sub_mode",
                      "projection_mode", "projection_mode_string", "magnification_index", "indicated_camera_length",
                      "indicated_magnification", "defocus", "objective_excitation", "intensity", "objective_stigmator",
                      "condenser_stigmator", "diffraction_shift", 'optics_state', 'state')

    PUT_V1_FORWARD = ("image_shift", "beam_shift", "beam_tilt", "projection_mode", "magnification_index",
                      "defocus", "intensity", "diffraction_shift", "objective_stigmator", "condenser_stigmator")

    def build_response(self, response):
        """Encode response and send to client"""
        if response is None:
            self.send_response(204)
            self.end_headers()
            return

        try:
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
                encoded_response = gzip_encode(encoded_response)
                content_encoding = 'gzip'
            else:
                content_encoding = None
        except Exception as exc:
            self.log_error("Exception raised during encoding of response: %s" % repr(exc))
            self.send_error(500, "Error handling request '%s': %s" % (self.path, str(exc)))
        else:
            self.send_response(200)
            if content_encoding:
                self.send_header('Content-Encoding', content_encoding)
            self.send_header('Content-Length', str(len(encoded_response)))
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(encoded_response)

    def do_GET_V1(self, endpoint, query):
        """Handle V1 GET requests"""
        if endpoint in self.GET_V1_FORWARD:
            response = getattr(self.server.microscope, 'get_' + endpoint)()
        elif endpoint.startswith("detector_param/"):
            name = unquote(endpoint[15:])
            response = self.server.microscope.get_detector_param(name)
        elif endpoint.startswith("camera_param/"):
            name = unquote(endpoint[13:])
            response = self.server.microscope.get_camera_param(name)
        elif endpoint.startswith("stem_detector_param/"):
            name = unquote(endpoint[20:])
            response = self.server.microscope.get_stem_detector_param(name)
        elif endpoint == "acquire":
            detectors = tuple(query.get("detectors", ()))
            response = self.server.microscope.acquire(*detectors)
        else:
            raise KeyError("Unknown endpoint: '%s'" % endpoint)
        return response

    def do_PUT_V1(self, endpoint, query):
        """Handle V1 PUT requests"""
        length = int(self.headers['Content-Length'])
        if length > 4096:
            raise ValueError("Too much content...")
        content = self.rfile.read(length)
        decoded_content = json.loads(content.decode("utf-8"))

        # Check for known endpoints
        response = None
        if endpoint in self.PUT_V1_FORWARD:
            response = getattr(self.server.microscope, 'set_' + endpoint)(decoded_content)
        elif endpoint == "stage_position":
            method = query.get("method", [None])[0]
            speed = query.get("speed", [None])[0]
            pos = dict((k, decoded_content[k]) for k in decoded_content.keys() if k in STAGE_AXES)
            self.server.microscope.set_stage_position(pos, method=method, speed=speed)
        elif endpoint.startswith("camera_param/"):
            name = unquote(endpoint[13:])
            ignore_errors = bool(query.get("ignore_errors", [False])[0])
            response = self.server.microscope.set_camera_param(name, decoded_content, ignore_errors=ignore_errors)
        elif endpoint.startswith("stem_detector_param/"):
            name = unquote(endpoint[20:])
            ignore_errors = bool(query.get("ignore_errors", [False])[0])
            response = self.server.microscope.set_stem_detector_param(name, decoded_content, ignore_errors=ignore_errors)
        elif endpoint == "stem_acquisition_param":
            ignore_errors = bool(query.get("ignore_errors", [False])[0])
            response = self.server.microscope.set_stem_acquisition_param(decoded_content, ignore_errors=ignore_errors)
        elif endpoint.startswith("detector_param/"):
            name = unquote(endpoint[15:])
            response = self.server.microscope.set_detector_param(name, decoded_content)
        elif endpoint == "normalize":
            self.server.microscope.normalize(decoded_content)
        else:
            raise KeyError("Unknown endpoint: '%s'" % endpoint)
        return response

    # Handler for the GET requests
    def do_GET(self):
        try:
            request = urlparse(self.path)
            if request.path.startswith("/v1/"):
                response = self.do_GET_V1(request.path[4:], parse_qs(request.query))
            else:
                raise KeyError('Unknown API version: %s' % self.path)
        except KeyError as exc:
            self.log_error("KeyError raised during handling of GET request '%s': %s" % (self.path, repr(exc)))
            self.send_error(404, str(exc))
        except Exception as exc:
            self.log_error("Exception raised during handling of GET request '%s': %s" % (self.path, repr(exc)))
            self.send_error(500, "Error handling request '%s': %s" % (self.path, str(exc)))
        else:
            self.build_response(response)

    # Handler for the PUT requests
    def do_PUT(self):
        try:
            request = urlparse(self.path)
            if request.path.startswith("/v1/"):
                response = self.do_PUT_V1(request.path[4:], parse_qs(request.query))
            else:
                raise KeyError('Unknown API version: %s' % self.path)
        except KeyError as exc:
            self.log_error("KeyError raised during handling of GET request '%s': %s" % (self.path, repr(exc)))
            self.send_error(404, str(exc))
        except Exception as exc:
            self.log_error("Exception raised during handling of GET request '%s': %s" % (self.path, repr(exc)))
            self.send_error(500, "Error handling request '%s': %s" % (self.path, str(exc)))
        else:
            self.build_response(response)


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
