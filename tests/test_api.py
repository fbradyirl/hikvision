"""
tests.test_api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests the api

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""
# pylint: disable=protected-access
import unittest
import openwebif.api
from openwebif.error import OpenWebIfError, MissingParamError
from requests.exceptions import ConnectionError

class TestAPI(unittest.TestCase):
    """ Tests openwebif.api module. """

    def test_create(self):
        """ Test creating a new device. """
        # Bogus config
        self.assertRaises(MissingParamError, lambda: openwebif.api.Client())
        self.assertRaises(OpenWebIfError, lambda: openwebif.api.Client('10.10.10.4'))

