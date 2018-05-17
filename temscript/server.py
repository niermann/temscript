#!/usr/bin/python
from __future__ import division, print_function
import numpy as np
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
    from urlparse import urlparse, parse_qs
    from urllib import pathname2url as quote
    from cStringIO import StringIO as BytesIO


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


def _parse_enum(type, item):
    """Try to parse 'item' (string or integer) to enum 'type'"""
    try:
        return type[item]
    except:
        return type(item)


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
        elif endpoint == "image_shift":
            response = self.server.microscope.get_image_shift()
        elif endpoint == "beam_shift":
            response = self.server.microscope.get_beam_shift()
        elif endpoint == "beam_tilt":
            response = self.server.microscope.get_beam_tilt()
        elif endpoint.startswith("detector_param/"):
            try:
                name = endpoint[15:]
                response = self.server.microscope.get_detector_param(name)
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
            pos = dict((k, decoded_content[k]) for k in decoded_content.keys() if k in Microscope.STAGE_AXES)
            self.server.microscope.set_stage_position(pos, method=method)
        elif endpoint == "image_shift":
            self.server.microscope.set_image_shift(decoded_content)
        elif endpoint == "beam_shift":
            self.server.microscope.set_beam_shift(decoded_content)
        elif endpoint == "beam_tilt":
            self.server.microscope.set_beam_tilt(decoded_content)
        elif endpoint.startswith("detector_param/"):
            try:
                name = endpoint[15:]
                response = self.server.microscope.set_detector_param(name, decoded_content)
            except KeyError:
                self.send_error(404, 'Unknown detector: %s' % self.path)
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
    def __init__(self, *args, **kw):
        microscope_factory = kw.pop("microscope_factory", None)
        if microscope_factory is None:
            from .microscope import Microscope
            microscope_factory = Microscope
        super(MicroscopeServer, self).__init__(*args, **kw)
        self.microscope = microscope_factory()


def run_server(argv=None, microscope_factory=None):
    """
    Main program for running the server

    :param argv: Arguments
    :type argv: List of str (see sys.argv)
    :param microscope_factory: Factory function for creation of microscope
    :type microscope_factory: callable without arguments
    :returns: Exit code
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080, help="Specify port on which the server is listening")
    parser.add_argument("--host", type=str, default='', help="Specify host address on which the the server is listening")
    args = parser.parse_args(argv)

    try:
        # Create a web server and define the handler to manage the incoming request
        server = MicroscopeServer((args.host, args.port), MicroscopeHandler, microscope_factory=microscope_factory)
        print("Started httpserver on host '%s' port %d." % (args.host, args.port))
        print("Press Ctrl+C to stop server.")

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('Ctrl+C received, shutting down the web server')
        server.socket.close()

    return 0


if __name__ == '__main__':
    run_server()
