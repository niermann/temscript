import socket
import json
from http.client import HTTPConnection
from urllib.parse import urlencode, quote_plus

from .base_microscope import BaseMicroscope
from .marshall import ExtendedJsonEncoder, unpack_array, gzip_decode, MIME_TYPE_PICKLE, MIME_TYPE_JSON


class RemoteMicroscope(BaseMicroscope):
    """
    Microscope-like class, which connects to a remote microscope server.

    :param address: (host, port) combination for the remote microscope.
    :type address: Tuple[str, int]
    :param transport: Underlying transport protocol, either 'JSON' (default) or 'PICKLE'
    :type transport: Literal['JSON', 'PICKLE']
    """
    def __init__(self, address, transport=None, timeout=None):
        self.address = address
        self.timeout = timeout
        self._conn = None
        if transport is None:
            transport = "JSON"
        if transport == "JSON":
            self.accepted_content = [MIME_TYPE_JSON]
        elif transport == "PICKLE":
            self.accepted_content = [MIME_TYPE_PICKLE]
        else:
            raise ValueError("Unknown transport protocol.")

        # Make connection
        self._conn = HTTPConnection(self.address[0], self.address[1], timeout=self.timeout)
        version_string = self.get_version()
        if int(version_string.split('.')[0]) < 2:
            raise ValueError("Expected microscope server version >= 2.0.0, actual version is %s" % version_string)

    def _request(self, method, endpoint, body=None, query=None, headers=None, accepted_response=None):
        """
        Send request to server.

        If accepted_response is None, 200 is accepted for all methods, additionally 204 is accepted
        for methods, which pass a body (PUT, PATCH, POST)

        :param method: HTTP method to use, e.g. "GET" or "PUT"
        :type method: str
        :param endpoint: URL to request
        :type endpoint: str
        :param query: Optional dict or iterable of key-value-tuples to encode as query
        :type: Union[Dict[str, str], Iterable[Tuple[str, str]], None]
        :param body: Body to send
        :type body: Optional[Union[str, bytes]]
        :param headers: Optional dict of additional headers.
        :type headers: Optional[Dict[str, str]]
        :param accepted_response: Accepted response codes
        :type accepted_response: Optional[List[int]]

        :returns: response, decoded response body
        """
        if accepted_response is None:
            accepted_response = [200]
            if method in ["PUT", "PATCH", "POST"]:
                accepted_response.append(204)

        # Create request
        headers = dict(headers) if headers is not None else dict()
        if "Accept" not in headers:
            headers["Accept"] = ",".join(self.accepted_content)
        if "Accept-Encoding" not in headers:
            headers["Accept-Encoding"] = "gzip"
        if query is not None:
            url = endpoint + '?' + urlencode(query)
        else:
            url = endpoint
        self._conn.request(method, url, body, headers)

        # Get response
        try:
            response = self._conn.getresponse()
        except socket.timeout:
            self._conn.close()
            self._conn = None
            raise

        if response.status not in accepted_response:
            if response.status == 404:
                raise KeyError("Failed remote call: %s" % response.reason)
            else:
                raise RuntimeError("Remote call returned status %d: %s" % (response.status, response.reason))
        if response.status == 204:
            return response, None

        # Decode response
        content_length = response.getheader("Content-Length")
        if content_length is not None:
            encoded_body = response.read(int(content_length))
        else:
            encoded_body = response.read()

        content_type = response.getheader("Content-Type")
        if content_type not in self.accepted_content:
            raise ValueError("Unexpected response type: %s", content_type)
        if response.getheader("Content-Encoding") == "gzip":
            encoded_body = gzip_decode(encoded_body)
        if content_type == MIME_TYPE_JSON:
            body = json.loads(encoded_body.decode("utf-8"))
        elif content_type == MIME_TYPE_PICKLE:
            import pickle
            body = pickle.loads(encoded_body)
        else:
            raise ValueError("Unsupported response type: %s", content_type)
        return response, body

    def _request_with_json_body(self, method, url, body, query=None, headers=None, accepted_response=None):
        """
        Like :meth:`_request` but body is encoded as JSON.

        ..see :: :meth:`_request`
        """
        if body is not None:
            headers = dict(headers) if headers is not None else dict()
            headers["Content-Type"] = MIME_TYPE_JSON
            encoder = ExtendedJsonEncoder()
            encoded_body = encoder.encode(body).encode("utf-8")
        else:
            encoded_body = None
        return self._request(method, url, body=encoded_body, query=query, headers=headers,
                             accepted_response=accepted_response)

    def get_family(self):
        return self._request("GET", "/v1/family")[1]

    def get_microscope_id(self):
        return self._request("GET", "/v1/microscope_id")[1]

    def get_version(self):
        return self._request("GET", "/v1/version")[1]

    def get_voltage(self):
        return self._request("GET", "/v1/voltage")[1]

    def get_vacuum(self):
        return self._request("GET", "/v1/vacuum")[1]

    def get_stage_holder(self):
        return self._request("GET", "/v1/stage_holder")[1]

    def get_stage_status(self):
        return self._request("GET", "/v1/stage_status")[1]

    def get_stage_limits(self):
        return self._request("GET", "/v1/stage_limits")[1]

    def get_stage_position(self):
        return self._request("GET", "/v1/stage_position")[1]

    def _set_stage_position(self, pos=None, method="GO", speed=None):
        query = {}
        if method is not None:
            query['method'] = method
        if speed is not None:
            query['speed'] = speed
        self._request_with_json_body("PUT", "/v1/stage_position", body=pos, query=query)

    def get_cameras(self):
        return self._request("GET", "/v1/cameras")[1]

    def get_stem_detectors(self):
        return self._request("GET", "/v1/stem_detectors")[1]

    def get_camera_param(self, name):
        return self._request("GET", "/v1/camera_param/" + quote_plus(name))[1]

    def set_camera_param(self, name, values, ignore_errors=None):
        query = None
        if ignore_errors is not None:
            query = {'ignore_errors': int(ignore_errors)}
        self._request_with_json_body("PUT", "/v1/camera_param/" + quote_plus(name), values, query=query)

    def get_stem_detector_param(self, name):
        return self._request("GET", "/v1/stem_detector_param/" + quote_plus(name))[1]

    def set_stem_detector_param(self, name, values, ignore_errors=None):
        query = None
        if ignore_errors is not None:
            query = {'ignore_errors': int(ignore_errors)}
        self._request_with_json_body("PUT", "/v1/stem_detector_param/" + quote_plus(name), values, query=query)

    def get_stem_acquisition_param(self):
        return self._request("GET", "/v1/stem_acquisition_param")[1]

    def set_stem_acquisition_param(self, values, ignore_errors=None):
        if ignore_errors is not None:
            query = {'ignore_errors': int(ignore_errors)}
        else:
            query = None
        self._request_with_json_body("PUT", "/v1/stem_acquisition_param", values, query=query)

    def acquire(self, *detectors):
        query = tuple(("detectors", det) for det in detectors)
        response, body = self._request("GET", "/v1/acquire", query=query)
        if response.getheader("Content-Type") == MIME_TYPE_JSON:
            body = {key: unpack_array(value) for key, value in body.items()}
        return body

    def get_image_shift(self):
        return self._request("GET", "/v1/image_shift")[1]

    def set_image_shift(self, pos):
        self._request_with_json_body("PUT", "/v1/image_shift", pos)

    def get_beam_shift(self):
        return self._request("GET", "/v1/beam_shift")[1]

    def set_beam_shift(self, pos):
        self._request_with_json_body("PUT", "/v1/beam_shift", pos)

    def get_beam_tilt(self):
        return self._request("GET", "/v1/beam_tilt")[1]

    def set_beam_tilt(self, pos):
        self._request_with_json_body("PUT", "/v1/beam_tilt", pos)

    def normalize(self, mode="ALL"):
        self._request_with_json_body("PUT", "/v1/normalize", mode)

    def get_projection_sub_mode(self):
        return self._request("GET", "/v1/projection_sub_mode")[1]

    def get_projection_mode(self):
        return self._request("GET", "/v1/projection_mode")[1]

    def set_projection_mode(self, mode):
        self._request_with_json_body("PUT", "/v1/projection_mode", mode)

    def get_projection_mode_string(self):
        return self._request("GET", "/v1/projection_mode_string")[1]

    def get_magnification_index(self):
        return self._request("GET", "/v1/magnification_index")[1]

    def set_magnification_index(self, index):
        self._request_with_json_body("PUT", "/v1/magnification_index", index)

    def get_indicated_camera_length(self):
        return self._request("GET", "/v1/indicated_camera_length")[1]

    def get_indicated_magnification(self):
        return self._request("GET", "/v1/indicated_magnification")[1]

    def get_defocus(self):
        return self._request("GET", "/v1/defocus")[1]

    def set_defocus(self, value):
        self._request_with_json_body("PUT", "/v1/defocus", value)

    def get_objective_excitation(self):
        return self._request("GET", "/v1/objective_excitation")[1]

    def get_intensity(self):
        return self._request("GET", "/v1/intensity")[1]

    def set_intensity(self, value):
        self._request_with_json_body("PUT", "/v1/intensity", value)

    def get_objective_stigmator(self):
        return self._request("GET", "/v1/objective_stigmator")[1]

    def set_objective_stigmator(self, value):
        self._request_with_json_body("PUT", "/v1/objective_stigmator", value)

    def get_condenser_stigmator(self):
        return self._request("GET", "/v1/condenser_stigmator")[1]

    def set_condenser_stigmator(self, value):
        self._request_with_json_body("PUT", "/v1/condenser_stigmator", value)

    def get_diffraction_shift(self):
        return self._request("GET", "/v1/diffraction_shift")[1]

    def set_diffraction_shift(self, value):
        self._request_with_json_body("PUT", "/v1/diffraction_shift", value)

    def get_screen_current(self):
        return self._request("GET", "/v1/screen_current")[1]

    def get_screen_position(self):
        return self._request("GET", "/v1/screen_position")[1]

    def set_screen_position(self, mode):
        self._request_with_json_body("PUT", "/v1/screen_position", mode)

    def get_illumination_mode(self):
        return self._request("GET", "/v1/illumination_mode")[1]

    def set_illumination_mode(self, mode):
        self._request_with_json_body("PUT", "/v1/illumination_mode", mode)

    def get_condenser_mode(self):
        return self._request("GET", "/v1/condenser_mode")[1]

    def set_condenser_mode(self, mode):
        self._request_with_json_body("PUT", "/v1/condenser_mode", mode)

    def get_stem_magnification(self):
        return self._request("GET", "/v1/stem_magnification")[1]

    def set_stem_magnification(self, value):
        self._request_with_json_body("PUT", "/v1/stem_magnification", value)

    def get_stem_rotation(self):
        return self._request("GET", "/v1/stem_rotation")[1]

    def set_stem_rotation(self, value):
        self._request_with_json_body("PUT", "/v1/stem_rotation", value)

    def get_illuminated_area(self):
        return self._request("GET", "/v1/illuminated_area")[1]

    def set_illuminated_area(self, value):
        self._request_with_json_body("PUT", "/v1/illuminated_area", value)

    def get_probe_defocus(self):
        return self._request("GET", "/v1/probe_defocus")[1]

    def set_probe_defocus(self, value):
        self._request_with_json_body("PUT", "/v1/probe_defocus", value)

    def get_convergence_angle(self):
        return self._request("GET", "/v1/convergence_angle")[1]

    def set_convergence_angle(self, value):
        self._request_with_json_body("PUT", "/v1/convergence_angle", value)

    def get_spot_size_index(self):
        return self._request("GET", "/v1/spot_size_index")[1]

    def set_spot_size_index(self, index):
        self._request_with_json_body("PUT", "/v1/spot_size_index", index)

    def get_dark_field_mode(self):
        return self._request("GET", "/v1/dark_field_mode")[1]

    def set_dark_field_mode(self, mode):
        self._request_with_json_body("PUT", "/v1/dark_field_mode", mode)

    def get_beam_blanked(self):
        return self._request("GET", "/v1/beam_blanked")[1]

    def set_beam_blanked(self, mode):
        self._request_with_json_body("PUT", "/v1/beam_blanked", mode)

    def is_stem_available(self):
        return self._request("GET", "/v1/stem_available")[1]

    def get_instrument_mode(self):
        return self._request("GET", "/v1/instrument_mode")[1]

    def set_instrument_mode(self, mode):
        self._request_with_json_body("PUT", "/v1/instrument_mode", mode)

    def get_state(self):
        return self._request("GET", "/v1/state")[1]
