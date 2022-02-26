from django.test import TestCase, override_settings
from mock import Mock

from garnett.middleware import get_language_from_request

class TestUtils(TestCase):
    def test_get_language_from_request(self):
        request = Mock()
        request.GET = {"glang": "en"}
        request.COOKIES = {"GARNETT_LANGUAGE_CODE": "de"}
        request.META = {"HTTP_X_GARNETT_LANGUAGE_CODE": "fr"}
        with override_settings(
            GARNETT_REQUEST_LANGUAGE_SELECTORS=[
                "garnett.selectors.cookie",
                "garnett.selectors.query",
                "garnett.selectors.header",
            ]
        ):
            self.assertTrue(get_language_from_request(request), "en")
        with override_settings(
            GARNETT_REQUEST_LANGUAGE_SELECTORS=[
                "garnett.selectors.cookie",
                "garnett.selectors.query",
                "garnett.selectors.header",
            ]
        ):
            self.assertTrue(get_language_from_request(request), "de")

        with override_settings(
            GARNETT_REQUEST_LANGUAGE_SELECTORS=[
                "garnett.selectors.header",
                "garnett.selectors.cookie",
                "garnett.selectors.query",
            ]
        ):
            self.assertTrue(get_language_from_request(request), "fr")
