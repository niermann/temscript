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
    from urlparse import urlparse, parse_qs, quote
    from cStringIO import StringIO as BytesIO

from temscript.microscope import Microscope

# Numpy array encoding JSON encoder
class ArrayJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            import sys, base64
            if obj.dtype.byteorder == '<':
                endian = "LITTLE"
            elif obj.dtype.byteorder == '>':
                endian = "BIG"
            else:
                endian = sys.byteorder.upper()
            return {
                'width': obj.shape[1],
                'height': obj.shape[0],
                'type': obj.dtype.name,
                'endianness': endian,
                'encoding': "BASE64",
                'data': base64.b64encode(obj).decode("ascii")
            }
        return json.JSONEncoder.default(self, obj)

# Setable object as ping-pong test thingie
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


class MicroscopeHandler(BaseHTTPRequestHandler):
    def send_array_dict(self, data, format):
        if format.startswith("PYTHON_PICKLE_V"):
            import pickle
            protocol = int(format[15:])
            content = pickle.dumps(data, protocol=protocol)
            self.send_response(200)
            self.send_header('Content-type', "application/python-pickle")
        elif format == "BASE64":

            response = {}
            for name, array in data.items():
                if array.dtype.byteorder == '<':
                    endian = "LITTLE"
                elif array.dtype.byteorder == '>':
                    endian = "BIG"
                else:
                    endian = sys.byteorder.upper()
                response[name] = {
                    'width': array.shape[1],
                    'height': array.shape[0],
                    'type': array.dtype.name,
                    'endianness': endian,
                    'encoding': "BASE64",
                    'data': base64.b64encode(array).decode("ascii")
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
        if endpoint == "family":
            response = self.server.microscope.get_family()
        elif endpoint == "vacuum":
            response = self.server.microscope.get_vacuum()
        elif endpoint == "detectors":
            response = self.server.microscope.get_detectors()
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
        elif endpoint == "test":
            response = _test
        else:
            self.send_error(404, 'Unknown endpoint: %s' % self.path)
            return

        if response is None:
            self.send_response(204)
            self.end_headers()
            return

        accept = [x.strip() for x in self.headers.get("Accept", "").split(",")]
        if "application/python-pickle" in accept:
            import pickle
            encoded_response = pickle.dumps(response, protocol=2)
            content_type = "application/python-pickle"
        else:
            encoded_response = ArrayJSONEncoder().encode(response).encode("utf-8")
            content_type = "application/json"
        self.send_response(200)
        self.send_header('Content-type', content_type)
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
                response = self.server.microscope.set_detector_param(name, decoded_content)
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
            return

        accept = [x.strip() for x in self.headers.get("Accept", "").split(",")]
        if "application/python-pickle" in accept:
            import pickle
            encoded_response = pickle.dumps(response, protocol=2)
            content_type = "application/python-pickle"
        else:
            encoded_response = ArrayJSONEncoder().encode(response).encode("utf-8")
            content_type = "application/json"
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(encoded_response)
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


class MicroscopeServer(HTTPServer):
    def __init__(self, *args, **kw):
        super(MicroscopeServer, self).__init__(*args, **kw)
        self.microscope = Microscope()


if __name__ == '__main__':
    SERVER_PORT = 8080
    SERVER_HOST = ''    # Empty is any interface

    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = MicroscopeServer((SERVER_HOST, SERVER_PORT), MicroscopeHandler)
        print("Started httpserver on host '%s' port %d." % (SERVER_HOST, SERVER_PORT))
        print("Press Ctrl+C to stop server.")

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('Ctrl+C received, shutting down the web server')
        server.socket.close()
