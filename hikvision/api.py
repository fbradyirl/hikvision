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
from hikvision.constants import DEFAULT_PORT
from requests.exceptions import ConnectionError as ReConnError
from requests.auth import HTTPBasicAuth

logging.basicConfig()
_LOGGING = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


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
    if response.error:
        _LOGGING.error("error %s", response.error)

def remove_namespace(response):
    return re.sub(' xmlns="[^"]+"', '', response, count=1)

class CameraClient(object):

    """
    CameraClient is the class handling the hikvision interactions.
    """

    def __init__(self, host=None, port=None,
                 username=None, password=None, is_https=True):
        _LOGGING.info("Initialising new hikvision camera client")

        if not host:
            _LOGGING.error('Missing hikvision host!')
            raise MissingParamError('Connection to hikvision failed.', None)

        self._username = username
        self._password = password

        # Now build base url
        self._base = build_url_base(host, port, is_https)

        try:
            _LOGGING.info("Going to probe device to test connection")
            version = self.get_firmware_version()
            _LOGGING.info("Connected OK!")
            _LOGGING.info("hikvision version %s", version)

        except ReConnError as conn_err:
            # _LOGGING.exception("Unable to connect to %s", host)
            raise hikvisionError('Connection to hikvision failed.', conn_err)


    def get_firmware_version(self):
        """
        Returns the firmware version running on the camera
        """
        return self.get_about(element_to_query='firmwareVersion')

    def get_about(self, element_to_query=None, timeout=None):
        """
        Returns ElementTree containing the result of 
        <host>/System/deviceInfo
        or if element_to_query is not None, the value of that element
        """

        url = '%s/System/deviceInfo' % self._base
        _LOGGING.info('url: %s', url)

        if timeout is not None:
            response = requests.get(url, auth=HTTPBasicAuth(
                self._username, self._password), 
                verify=False, timeout=timeout)
        else:
            response = requests.get(url, auth=HTTPBasicAuth(
                self._username, self._password), 
                verify=False)

        _LOGGING.info('response: %s', response)
        _LOGGING.info("status_code %s", response.status_code)

        if response.status_code != 200:
            log_response_errors(response)
            return None

        if element_to_query is None:
            return response.content
        else:
            try:
                tree = ElementTree.fromstring(remove_namespace(response.content))
                result = tree.findall('%s' % (element_to_query))
                
                if len(result) > 0:
                    _LOGGING.info('element_to_query: %s result: %s',
                                  element_to_query, result[0])

                    return result[0].text.strip()
                else:
                    _LOGGING.error(
                        'There was a problem finding element: %s',
                        element_to_query)
                    _LOGGING.error('Entire response: %s', response.content)

            except AttributeError as attib_err:
                _LOGGING.error('Entire response: %s', response.content)
                _LOGGING.error(
                    'There was a problem finding element:'
                    ' %s AttributeError: %s', element_to_query, attib_err)
                return
        return
