"""
hikvision.api
~~~~~~~~~~~~~~~~~~~~

Provides methods for interacting with hikvision

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""

import logging
import requests
import re
from xml.etree import ElementTree
from hikvision.error import HikvisionError, MissingParamError
from hikvision.constants import DEFAULT_PORT, DEFAULT_HEADERS
from requests.exceptions import ConnectionError as ReConnError
from requests.auth import HTTPBasicAuth

_LOGGING = logging.getLogger(__name__)

# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes


def build_url_base(host, port, is_https):
    """
    Make base of url based on config
    """
    base = "http"
    if is_https:
        base += 's'

    base += "://"
    base += host

    if port:
        base += ":"
        base += str(port)

    return base


def log_response_errors(response):
    """
    Logs problems in a response
    """

    _LOGGING.error("status_code %s", response.status_code)


def enable_logging():
    """ Setup the logging for home assistant. """
    logging.basicConfig(level=logging.DEBUG)


def remove_namespace(response):
    """ Removes namespace element from xml"""
    return re.sub(' xmlns="[^"]+"', '', response, count=1)


class CreateDevice(object):

    """
    Creates a new camera api device
    """

    def __init__(self, host=None, port=DEFAULT_PORT,
                 username=None, password=None, is_https=False):
        enable_logging()
        _LOGGING.info("Initialising new hikvision camera client")

        if not host:
            _LOGGING.error('Missing hikvision host!')
            raise MissingParamError('Connection to hikvision failed.', None)

        self._username = username
        self._host = host
        self._password = password
        self.xml_motion_detection_off = None
        self.xml_motion_detection_on = None

        # Now build base url
        self._base = build_url_base(host, port, is_https)

        # need to support different channel
        self.motion_url = '%s/MotionDetection/1' % self._base
        _LOGGING.info('motion_url: %s', self.motion_url)

        self._xml_namespace = "http://www.hikvision.com/ver10/XMLSchema"
        # Required to parse and change xml with the host camera
        _LOGGING.info(
            'ElementTree.register_namespace: %s', self._xml_namespace)
        ElementTree.register_namespace("", self._xml_namespace)

        try:
            _LOGGING.info("Going to probe device to test connection")
            version = self.get_version()
            enabled = self.is_motion_detection_enabled()
            _LOGGING.info("Connected OK!")
            _LOGGING.info("Camera firmaward version: %s", version)
            _LOGGING.info("Motion Detection enabled: %s", enabled)

        except ReConnError as conn_err:
            # _LOGGING.exception("Unable to connect to %s", host)
            raise HikvisionError('Connection to hikvision failed.', conn_err)

    def get_version(self):
        """
        Returns the firmware version running on the camera
        """
        return self.get_about(element_to_query='firmwareVersion')

    def get_about(self, element_to_query=None):
        """
        Returns ElementTree containing the result of
        <host>/System/deviceInfo
        or if element_to_query is not None, the value of that element
        """

        url = '%s/System/deviceInfo' % self._base
        _LOGGING.info('url: %s', url)

        response = requests.get(
            url, auth=HTTPBasicAuth(self._username, self._password))

        _LOGGING.debug('response: %s', response)
        _LOGGING.debug("status_code %s", response.status_code)

        if response.status_code != 200:
            log_response_errors(response)
            return None

        if element_to_query is None:
            return response.text
        else:
            try:
                tree = ElementTree.fromstring(response.text)

                element_to_query = './/{%s}%s' % (
                    self._xml_namespace, element_to_query)
                result = tree.findall(element_to_query)
                if len(result) > 0:
                    _LOGGING.debug('element_to_query: %s result: %s',
                                   element_to_query, result[0])

                    return result[0].text.strip()
                else:
                    _LOGGING.error(
                        'There was a problem finding element: %s',
                        element_to_query)
                    _LOGGING.error('Entire response: %s', response.text)

            except AttributeError as attib_err:
                _LOGGING.error('Entire response: %s', response.text)
                _LOGGING.error(
                    'There was a problem finding element:'
                    ' %s AttributeError: %s', element_to_query, attib_err)
                return
        return

    def is_motion_detection_enabled(self):
        """ Get current state of Motion Detection """

        response = requests.get(self.motion_url, auth=HTTPBasicAuth(
            self._username, self._password))
        _LOGGING.debug('Response: %s', response.text)

        if response.status_code != 200:
            _LOGGING.error(
                "There was an error connecting to %s", self.motion_url)
            _LOGGING.error("status_code %s", response.status_code)
            return

        try:

            tree = ElementTree.fromstring(response.text)
            find_result = tree.findall('.//{%s}enabled' % self._xml_namespace)
            if len(find_result) == 0:
                _LOGGING.error("Problem getting motion detection status")
                return

            result = find_result[0].text.strip()
            _LOGGING.info(
                'Current motion detection state? enabled: %s', result)

            if result == 'true':
                # Save this for future switch off
                self.xml_motion_detection_on = ElementTree.tostring(
                    tree)
                find_result[0].text = 'false'
                self.xml_motion_detection_off = ElementTree.tostring(
                    tree)
                return True
            else:
                # Save this for future switch on
                self.xml_motion_detection_off = ElementTree.tostring(
                    tree)
                find_result[0].text = 'true'
                self.xml_motion_detection_on = ElementTree.tostring(
                    tree)
                return False

        except AttributeError as attib_err:
            _LOGGING.error(
                'There was a problem parsing '
                'camera motion detection state: %s', attib_err)
            return

    def enable_motion_detection(self):
        """ Enable Motion Detection """

        self.put_motion_detection_xml(self.xml_motion_detection_on)

    def disable_motion_detection(self):
        """ Disable Motion Detection """

        self.put_motion_detection_xml(self.xml_motion_detection_off)

    def put_motion_detection_xml(self, xml):
        """ Put request with xml Motion Detection """

        _LOGGING.debug('xml:')
        _LOGGING.debug("%s", xml)

        headers = DEFAULT_HEADERS
        headers['Content-Length'] = len(xml)
        headers['Host'] = self._host
        response = requests.patch(self.motion_url, auth=HTTPBasicAuth(
            self._username, self._password), data=xml, headers=headers)
        _LOGGING.debug('request.headers:')
        _LOGGING.debug('%s', response.request.headers)
        _LOGGING.debug('Response:')
        _LOGGING.debug('%s', response.text)

        if response.status_code != 200:
            _LOGGING.error(
                "There was an error connecting to %s", self.motion_url)
            _LOGGING.error("status_code %s", response.status_code)
            return

        try:
            tree = ElementTree.fromstring(response.text)
            find_result = tree.findall(
                './/{%s}statusString' % self._xml_namespace)
            if len(find_result) == 0:
                _LOGGING.error("Problem getting motion detection status")
                return

            if find_result[0].text.strip() == 'OK':
                _LOGGING.info('Updated successfully')

        except AttributeError as attib_err:
            _LOGGING.error(
                'There was a problem parsing the response: %s', attib_err)
            return
