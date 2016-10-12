#!/usr/bin/python
from __future__ import division, print_function
import numpy as np
import json

# Get imports from library
try:
    # Python 3.X
    from http.client import HTTPConnection
    from urllib.parse import urlencode
    from io import BytesIO
except ImportError:
    # Python 2.X
    from httplib import HTTPConnection
    from urlparse import urlencode
    from cStringIO import StringIO as BytesIO


class MicroscopeClient(object):
    def __init__(self, address, transport="JSON"):
        self.host = address[0]
        self.port = address[1]
        self._conn = None
        if transport == "JSON":
            self.accepted_content = ["application/json"]
        elif transport == "PICKLE":
            self.accepted_content = ["application/python-pickle"]

    def _request(self, method, endpoint, query={}, body=None, headers={}, accepted_response=[200]):
        # Make connection
        if self._conn is None:
            self._conn = HTTPConnection(self.host, self.port)

        # Create request
        if len(query) > 0:
            url = "%s?%s" % (endpoint, urlencode(query))
        else:
            url = endpoint
        headers = dict(headers)
        if "Accept" not in headers:
            headers["Accept"] = ",".join(self.accepted_content)
        if "Accept-Encoding" not in headers:
            headers["Accept-Encoding"] = "gzip"
        self._conn.request(method, url, body, headers)

        # Get response
        response = self._conn.getresponse()
        body = response.read()
        if response.status not in accepted_response:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))
        if response.status == 204:
            return response, body

        # Decode response
        content_type = response.getheader("Content-Type")
        if content_type not in self.accepted_content:
            raise ValueError("Unexpected response type: %s", content_type)
        if response.getheader("Content-Encoding") == "gzip":
            import zlib
            body = zlib.decompress(body, 16 + zlib.MAX_WBITS)
        if content_type == "application/json":
            body = json.loads(body.decode("utf-8"))
        elif content_type == "application/python-pickle":
            import pickle
            body = pickle.loads(body)
        else:
            raise ValueError("Unsupported response type: %s", content_type)
        return response, body

    def get_test(self):
        response, body = self._request("GET", "/v1/test")
        return body

    def set_test(self, value):
        content = json.dumps(value).encode("utf-8")
        self._request("PUT", "/v1/test", body=content, accepted_response=[200, 204],
                      headers={"Content-Type": "application/json"})

    def get_family(self):
        response, body = self._request("GET", "/v1/family")
        return body

    def get_stage_holder(self):
        response, body = self._request("GET", "/v1/stage_holder")
        return body

    def get_stage_status(self):
        response, body = self._request("GET", "/v1/stage_status")
        return body

    def get_stage_limits(self):
        response, body = self._request("GET", "/v1/stage_limits")
        return body

    def get_stage_position(self):
        response, body = self._request("GET", "/v1/stage_position")
        return body

    def set_stage_position(self, pos, method=None):
        pos = dict(pos)
        if method is not None:
            pos["method"] = method
        elif "method" in pos:
            del pos["method"]
        content = json.dumps(param).encode("utf-8")
        self._request("PUT", "/v1/stage_position", body=content, accepted_response=[200, 204],
                      headers={"Content-Type": "application/json"})

    def get_vacuum(self):
        response, body = self._request("GET", "/v1/vacuum")
        return body

    def get_detectors(self):
        response, body = self._request("GET", "/v1/detectors")
        return body

    def get_detector_param(self, name):
        response, body = self._request("GET", "/v1/detector_param/" + name)
        return body

    def set_detector_param(self, name, param):
        content = json.dumps(param).encode("utf-8")
        self._request("PUT", "/v1/detector_param/" + name, body=content, accepted_response=[200, 204],
                      headers={"Content-Type": "application/json"})

    allowed_types = {"INT8", "INT16", "INT32", "INT64", "UINT8", "UINT16", "UINT32", "UINT64", "FLOAT32", "FLOAT64"}
    allowed_endianness = {"LITTLE", "BIG"}

    def acquire(self, *detectors):
        query = [("detectors", det) for det in detectors]
        response, body = self._request("GET", "/v1/acquire", query=query)
        if response.getheader("Content-Type") == "application/json":
            # Unpack array
            import sys
            import base64
            endianness = sys.byteorder.upper()
            result = {}
            for k, v in body.items():
                shape = int(v["height"]), int(v["width"])
                if v["type"] not in self.allowed_types:
                    raise ValueError("Unsupported array type in JSON stream: %s" % str(v["type"]))
                if v["endianness"] not in self.allowed_endianness:
                    raise ValueError("Unsupported endianness in JSON stream: %s" % str(v["endianness"]))
                dtype = np.dtype(v["type"].lower())
                if v["encoding"] == "BASE64":
                    data = base64.b64decode(v["data"])
                else:
                    raise ValueError("Unsupported encoding of array in JSON stream: %s" % str(v["encoding"]))
                data = np.frombuffer(data, dtype=dtype).reshape(*shape)
                if v["endianness"] != endianness:
                    data = data.byteswap()
                result[k] = data
            body = result
        return body


if __name__ == '__main__':
    SERVER_PORT = 8080
    SERVER_HOST = '192.168.99.10' #'localhost'

    client = MicroscopeClient((SERVER_HOST, SERVER_PORT))
    print(client.get_test())
    client.set_test({"EINS": 1, "ZWEI": 2.0, "DREI": "xxx", "VIER": [0,1,2,3]})
    print(client.get_family())
    print(client.get_test())
    print(client.get_vacuum())
    print(client.get_detectors())
    param = client.get_detector_param("CCD")
    print(param)
    exposure = 1.0 if param["exposure(s)"] != 1.0 else 1.0 / param["exposure(s)"]
    client.set_detector_param("CCD", {"exposure(s)": exposure})
    print(client.get_detector_param("CCD"))
    images = client.acquire("CCD")
    print(images["CCD"].shape, images["CCD"].dtype)

    import matplotlib.pyplot as plt

    plt.imshow(images["CCD"], cmap="gray")
    plt.show()