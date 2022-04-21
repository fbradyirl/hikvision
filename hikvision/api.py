"""
hikvision.api
~~~~~~~~~~~~~~~~~~~~

Provides methods for interacting with hikvision

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""

import logging
from xml.etree import ElementTree
import re

import requests
from requests.exceptions import ConnectionError as ReConnError
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from hikvision.error import HikvisionError, MissingParamError
from hikvision.constants import DEFAULT_PORT, DEFAULT_HEADERS, XML_ENCODING
from hikvision.constants import DEFAULT_SENS_LEVEL

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
    return re.sub(' xmlns="[^"]+"', '', response)


def tree_no_ns_from_string(response):
    """ Removes namespace element from response"""
    text = remove_namespace(response)
    return ElementTree.fromstring(text)


class CreateDevice:

    """
    Creates a new camera api device
    """

    def __init__(self, host=None, port=DEFAULT_PORT,
                 username=None, password=None, is_https=False,
                 sensitivity_level=DEFAULT_SENS_LEVEL,
                 digest_auth=True, strict_isapi=True):
        enable_logging()
        _LOGGING.info("Initialising new hikvision camera client")

        if not host:
            _LOGGING.error('Missing hikvision host!')
            raise MissingParamError('Connection to hikvision failed.', None)

        if not digest_auth and not is_https:
            _LOGGING.warning("%s: HTTP Basic Auth without SSL is insecure",
                             host)

        self._username = username
        self._host = host
        self._password = password
        self._sensitivity_level = sensitivity_level
        self._digest_auth = digest_auth
        self._strict_isapi = strict_isapi
        self._auth_fn = HTTPDigestAuth if self._digest_auth else HTTPBasicAuth
        self.xml_motion_detection_off = None
        self.xml_motion_detection_on = None
        self.xml_overlays_off = None
        self.xml_overlays_on = None

        # Now build base url
        self._base = build_url_base(host, port, is_https)

        # need to support different channel
        if self._strict_isapi:
            self.motion_url = (
                '%s/ISAPI/System/Video/Inputs/channels/1/motionDetection' %
                self._base)
            self.channel_name_overlay_url = (
                '%s/ISAPI/System/Video/inputs/channels/1/overlays/channelNameOverlay' %
                self._base)
            self.date_time_overlay_url = (
                '%s/ISAPI/System/Video/inputs/channels/1/overlays/dateTimeOverlay' %
                self._base)
            self.deviceinfo_url = '%s/ISAPI/System/deviceInfo' % self._base
#            self._xml_namespace = "{http://www.hikvision.com/ver20/XMLSchema}"
        else:
            self.motion_url = '%s/MotionDetection/1' % self._base
            self.channel_name_overlay_url = '%s/overlays/channelNameOverlay' % self._base
            self.date_time_overlay_url = '%s/overlays/dateTimeOverlay' % self._base
            self.deviceinfo_url = '%s/System/deviceInfo' % self._base
#            self._xml_namespace = "{http://www.hikvision.com/ver10/XMLSchema}"
        self._xml_namespace = ""
        _LOGGING.info('motion_url: %s', self.motion_url)
        _LOGGING.info('channel_name_overlay_url: %s', self.channel_name_overlay_url)
        _LOGGING.info('date_time_overlay_url: %s', self.date_time_overlay_url)

        # Required to parse and change xml with the host camera
        # _LOGGING.info(
        #    'ElementTree.register_namespace: %s', self._xml_namespace)
        # ElementTree.register_namespace("", self._xml_namespace)

        try:
            _LOGGING.info("Going to probe device to test connection")
            version = self.get_version()
            enabled = self.is_motion_detection_enabled()
            _LOGGING.info("%s Connected OK! firmware = %s, "
                          "motion detection enabled = %s", self._host,
                          version, enabled)

        except ReConnError as conn_err:
            raise HikvisionError('Connection to hikvision %s failed' %
                                 self._host, conn_err) from conn_err


    def get_isapi_content(self, url):
        """Get content."""

        response = requests.get(url, auth=self._auth_fn(
            self._username, self._password))
        _LOGGING.debug('Response: %s', response.text)

        if response.status_code != 200:
            _LOGGING.error(
                "%s: Error connecting to %s: status_code = %s",
                self._host, self.motion_url, response.status_code)
            raise Exception()
        
        return response.text

    def post_isapi_data(self, url, data):
        """Get content."""

        headers = DEFAULT_HEADERS
        headers['Content-Length'] = str(len(data))
        headers['Host'] = self._host
        response = requests.put(url, auth=self._auth_fn(
            self._username, self._password), data=data, headers=headers)

        if response.status_code != 200:
            _LOGGING.error(
                "%s: Error connecting to %s: status_code = %s",
                self._host, self.motion_url, response.status_code)
            raise Exception()

        _LOGGING.debug('request.headers:')
        _LOGGING.debug('%s', response.request.headers)
        _LOGGING.debug('Response:')
        _LOGGING.debug('%s', response.text)
        
        return response.text

    def get_xml_tree(self, url):
        return tree_no_ns_from_string(self.get_isapi_content(url))

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

        text = self.get_isapi_content(self.deviceinfo_url)

        if element_to_query is None:
            return text
        
        try:
            tree = tree_no_ns_from_string(text)

            element_to_query = './/%s%s' % (
                self._xml_namespace, element_to_query)
            result = tree.findall(element_to_query)
            if len(result) > 0:
                _LOGGING.debug('element_to_query: %s result: %s',
                               element_to_query, result[0])

                return result[0].text.strip()
            _LOGGING.error(
                'There was a problem finding element: %s',
                element_to_query)
            _LOGGING.error('Entire response: %s', response.text)

        except AttributeError as attib_err:
            _LOGGING.error('Entire response: %s', response.text)
            _LOGGING.error(
                'There was a problem finding element:'
                ' %s AttributeError: %s', element_to_query, attib_err)
            return None
        return None

    def get_bool_value(self, tree, name):
        element = tree.findall('.//%s%s' % (self._xml_namespace, name))
        assert(len(element) == 1)
        return element[0].text.strip().lower() == 'true'

    def set_bool_value(self, tree, name, value: bool):
        element = tree.findall('.//%s%s' % (self._xml_namespace, name))
        assert(len(element) == 1)
        element[0].text = str(value).lower()
        return tree

    def get_int_value(self, tree, name):
        enabled_element = tree.findall('.//%s%s' % (self._xml_namespace, name))
        assert(len(enabled_element) == 1)
        return int(enabled_element[0].text.strip())

    def set_int_value(self, tree, name, value: int):
        enabled_element = tree.findall('.//%s%s' % (self._xml_namespace, name))
        assert(len(enabled_element) == 1)
        enabled_element[0].text = str(value)
        return tree

    def is_motion_detection_enabled(self):
        """Get current state of Motion Detection.

        Returns False on error or if motion detection is off."""

        tree = self.get_xml_tree(self.motion_url)

        try:
            enabled = self.get_bool_value(tree, 'enabled')
            sensitivity_level = self.get_int_value(tree, 'sensitivityLevel')
            
            _LOGGING.info('%s motion detection state, enabled: %s', self._host, str(enabled))

            return enabled
        except AttributeError as attib_err:
            _LOGGING.error('%s: Problem parsing camera motion detection state: %s', self._host, attib_err)
            return False

    def is_channel_name_overlay_enabled(self):
        """Get current state of Motion Detection.

        Returns False on error or if motion detection is off."""

        tree = self.get_xml_tree(self.channel_name_overlay_url)

        try:
            enabled = self.get_bool_value(tree, 'enabled')
            
            _LOGGING.info('%s enabled: %s', self._host, str(enabled))

            return enabled
        except AttributeError as attib_err:
            _LOGGING.error('%s: Problem parsing camera motion detection state: %s', self._host, attib_err)
            return False

    def is_date_time_overlay_enabled(self):
        """Get current state of Motion Detection.

        Returns False on error or if motion detection is off."""
        tree = self.get_xml_tree(self.date_time_overlay_url)

        try:
            enabled = self.get_bool_value(tree, 'enabled')
            
            _LOGGING.info('%s enabled: %s', self._host, str(enabled))

            return enabled
        except AttributeError as attib_err:
            _LOGGING.error('%s: Problem parsing camera motion detection state: %s', self._host, attib_err)
            return False

    def set_motion_detection(self, value: bool):
        """ Enable Motion Detection """

        tree = self.get_xml_tree(self.motion_url)
        tree = self.set_bool_value(tree, 'enabled', value)        

        self.put_tree(self.motion_url, tree)

    def set_channel_name_overlay(self, value: bool):
        """ Enable Motion Detection """

        tree = self.get_xml_tree(self.channel_name_overlay_url)
        tree = self.set_bool_value(tree, 'enabled', value)        

        self.put_tree(self.channel_name_overlay_url, tree)

    def set_date_time_overlay(self, value: bool):
        """ Enable Motion Detection """

        tree = self.get_xml_tree(self.date_time_overlay_url)
        tree = self.set_bool_value(tree, 'enabled', value)        

        self.put_tree(self.date_time_overlay_url, tree)

    def put_tree(self, url, tree):
        """ Put request with xml """
        xml = ElementTree.tostring(tree, encoding=XML_ENCODING)

        _LOGGING.debug('xml:')
        _LOGGING.debug("%s", xml)

        text = self.post_isapi_data(url, xml)

        try:
            tree = tree_no_ns_from_string(text)
            enabled_element = tree.findall(
                './/%sstatusString' % self._xml_namespace)
            if len(enabled_element) == 0:
                _LOGGING.error("%s: Problem getting motion detection status",
                               self._host)
                return

            if enabled_element[0].text.strip() == 'OK':
                _LOGGING.info('Updated successfully')

        except AttributeError as attrib_err:
            _LOGGING.error(
                '%s: Problem parsing the response: %s',
                self._host, attrib_err)
            return