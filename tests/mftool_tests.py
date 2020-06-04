"""
    This is a test module for testing
"""
import unittest
import logging
import json
import six
from mftool import Mftool
from bs4 import BeautifulSoup

log = logging.getLogger('mftool')
logging.basicConfig(level=logging.DEBUG)


class TestAPIs(unittest.TestCase):
    def setUp(self):
        self.mftool = Mftool()

    def test_get_scheme_codes(self):
        sc = self.mftool.get_scheme_codes()
        self.assertIsNotNone(sc)
        self.assertIsInstance(sc, dict)
        # test the json format return
        sc_json = self.mftool.get_scheme_codes(as_json=True)
        self.assertIsInstance(sc_json, str)
        # reconstruct the dict from json and compare
        six.assertCountEqual(self, sc, json.loads(sc_json))

    def test_is_valid_code(self):
        code = '119598'
        self.assertTrue(self.mftool.is_valid_code(code))

    def test_negative_is_valid_code(self):
        wrong_code = '1195'
        self.assertFalse(self.mftool.is_valid_code(wrong_code))

    def test_get_scheme_quote(self):
        code = '101305'
        self.assertIsInstance(self.mftool.get_scheme_quote(code), dict)
        # with json respomftool
        self.assertIsInstance(self.mftool.get_scheme_quote(code, as_json=True),str)
        # with wrong code
        code = 'wrong code'
        self.assertIsNone(self.mftool.get_scheme_quote(code))
        # with code in 'int' format
        code = 101305
        self.assertIsInstance(self.mftool.get_scheme_quote(code), dict)

    def test_get_scheme_historical_nav(self):
        code = '101305'
        self.assertIsInstance(self.mftool.get_scheme_historical_nav(code), dict)
        # with json respomftool
        self.assertIsInstance(self.mftool.get_scheme_historical_nav(code, as_json=True), str)
        # with wrong code
        code = 'wrong code'
        self.assertIsNone(self.mftool.get_scheme_historical_nav(code))
        # with code in 'int' format
        code = 101305
        self.assertIsInstance(self.mftool.get_scheme_historical_nav(code), dict)

    def test_get_scheme_details(self):
        code = '101305'
        self.assertIsInstance(self.mftool.get_scheme_details(code), dict)
        # with json respomftool
        self.assertIsInstance(self.mftool.get_scheme_details(code, as_json=True), str)
        # with wrong code
        code = 'wrong code'
        self.assertIsNone(self.mftool.get_scheme_details(code))
        # with code in 'int' format
        code = 101305
        self.assertIsInstance(self.mftool.get_scheme_details(code), dict)

# TODO: test calculate_balance_units_value


if __name__ == '__main__':
    unittest.main()
