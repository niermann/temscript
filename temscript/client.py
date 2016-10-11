#!/usr/bin/python
from __future__ import division, print_function
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


class TemscriptClient(object):
    def __init__(self, address):
        self.host = address[0]
        self.port = address[1]
        self._conn = None

    def _request(self, method, endpoint, query={}, body=None, headers={}):
        if self._conn is None:
            self._conn = HTTPConnection(self.host, self.port)
        if len(query) > 0:
            url = "%s?%s" % (endpoint, urlencode(query))
        else:
            url = endpoint
        self._conn.request(method, url, body, headers)
        return self._conn.getresponse()

    def get_test(self):
        response = self._request("GET", "/v1/test")
        body = response.read()
        if response.status != 200:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))
        if response.getheader("Content-type") != "application/json":
            raise ValueError("Unexpected response type: %s", response.getheader("Content-type"))
        return json.loads(body.decode("utf-8"))

    def put_test(self, value):
        content = json.dumps(value).encode("utf-8")
        response = self._request("PUT", "/v1/test", body=content, headers={"Content-Type": "application/json"})
        response.read()
        if response.status < 200 or response.status >= 300:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))

    def get_vacuum(self):
        response = self._request("GET", "/v1/vacuum")
        body = response.read()
        if response.status != 200:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))
        if response.getheader("Content-type") != "application/json":
            raise ValueError("Unexpected response type: %s", response.getheader("Content-type"))
        return json.loads(body.decode("utf-8"))

    def get_detectors(self):
        response = self._request("GET", "/v1/detectors")
        body = response.read()
        if response.status != 200:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))
        if response.getheader("Content-type") != "application/json":
            raise ValueError("Unexpected response type: %s", response.getheader("Content-type"))
        return json.loads(body.decode("utf-8"))

    def get_detector_param(self, name):
        response = self._request("GET", "/v1/detector_param/" + name)
        body = response.read()
        if response.status != 200:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))
        if response.getheader("Content-type") != "application/json":
            raise ValueError("Unexpected response type: %s", response.getheader("Content-type"))
        return json.loads(body.decode("utf-8"))

    def put_detector_param(self, name, param):
        content = json.dumps(param).encode("utf-8")
        response = self._request("PUT", "/v1/detector_param/" + name, body=content, headers={"Content-Type": "application/json"})
        response.read()
        if response.status < 200 or response.status >= 300:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))

    def acquire(self, detectors):
        headers = {"Content-Type": "application/json",
                   }#"Accept-Encoding": "gzip"}
        query = [("detectors", det) for det in detectors]
        query.append(("format", "PYTHON_PICKLE_V2"))
        response = self._request("GET", "/v1/acquire", query=query, headers=headers)
        if response.getheader("Content-Encoding") == "gzip":
            import zlib
            body = zlib.decompress(response.read(), 16 + zlib.MAX_WBITS)
        else:
            body = response.read()
        if response.status != 200:
            raise ValueError("Failed remote call: %d, %s" % (response.status, response.reason))
        if response.getheader("Content-type") == "application/python-pickle":
            import pickle
            return pickle.loads(body)
        else:
            raise ValueError("Unexpected response type: %s", response.getheader("Content-type"))


if __name__ == '__main__':
    SERVER_PORT = 8080
    SERVER_HOST = '192.168.99.10' #'localhost'

    client = TemscriptClient((SERVER_HOST, SERVER_PORT))
    print(client.get_test())
    client.put_test({"EINS": 1, "ZWEI": 2.0, "DREI": "xxx", "VIER": [0,1,2,3]})
    print(client.get_test())
    print(client.get_vacuum())
    print(client.get_detectors())
    param = client.get_detector_param("CCD")
    print(param)
    exposure = 1.0 if param["exposure_s"] != 1.0 else 1.0 / param["exposure_s"]
    client.put_detector_param("CCD", {"exposure_s": exposure})
    print(client.get_detector_param("CCD"))
    images = client.acquire(["CCD"])
    print(images["CCD"].shape, images["CCD"].dtype)

    import matplotlib.pyplot as plt

    plt.imshow(images["CCD"], cmap="gray")
    plt.show()
