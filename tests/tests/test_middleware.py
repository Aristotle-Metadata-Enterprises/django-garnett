from django.test import Client, TestCase, RequestFactory
from django.http import HttpResponse, Http404

from garnett.middleware import (
    TranslationContextMiddleware,
    TranslationContextNotFoundMiddleware,
)
from garnett.utils import get_current_language


class TestTranslationContextMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TranslationContextMiddleware(lambda r: HttpResponse("Nice"))
        self.not_found_middleware = TranslationContextNotFoundMiddleware(
            lambda r: HttpResponse("Nice")
        )

    def test_sets_language_context(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("garnett_languages" in response.context.keys())
        self.assertTrue("garnett_current_language" in response.context.keys())

    def test_translation_middleware_sets_language(self):
        def test_view(request):
            lang = get_current_language()
            self.assertEqual(lang, "de")
            return HttpResponse("Nice")

        middleware = TranslationContextMiddleware(test_view)
        middleware(self.factory.get("/home?glang=de"))

    def test_translation_middleware_sets_cookie(self):
        response = self.middleware(self.factory.get("/home?glang=de"))
        self.assertIn("GARNETT_LANGUAGE_CODE", response.cookies)
        self.assertEqual(response.cookies["GARNETT_LANGUAGE_CODE"].value, "de")

    def test_not_found_middleware_valid_lang(self):
        """Test that the not found middleware returns response when given valid language"""
        response = self.not_found_middleware(self.factory.get("/home?glang=de"))
        self.assertEqual(response.content, b"Nice")

    def test_not_found_middleware_invalid_lang(self):
        """Test that the not found middleware 404's when given invalid language"""
        with self.assertRaises(Http404):
            self.not_found_middleware(self.factory.get("/home?glang=notalang"))
