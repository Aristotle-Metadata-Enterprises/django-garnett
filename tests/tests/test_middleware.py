from django.test import Client, TestCase, RequestFactory
from django.http import HttpResponse, Http404

from garnett.middleware import (
    TranslationContextMiddleware,
    TranslationContextNotFoundMiddleware,
    TranslationCacheMiddleware,
)
from garnett.utils import get_current_language_code


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
            lang = get_current_language_code()
            self.assertEqual(lang, "de")
            return HttpResponse("Nice")

        middleware = TranslationContextMiddleware(test_view)
        middleware(self.factory.get("/home?glang=de"))

    def test_not_found_middleware_valid_lang(self):
        """Test that the not found middleware returns response when given valid language"""
        response = self.not_found_middleware(self.factory.get("/home?glang=de"))
        self.assertEqual(response.content, b"Nice")

    def test_not_found_middleware_invalid_lang(self):
        """Test that the not found middleware 404's when given invalid language"""
        with self.assertRaises(Http404):
            self.not_found_middleware(self.factory.get("/home?glang=notalang"))


class TestTranslationCacheMiddleware(TestCase):
    def setUp(self):
        self.middleware = TranslationCacheMiddleware(lambda r: HttpResponse("Nice"))
        self.factory = RequestFactory()

    def test_cache_middleware_sets_session_value(self):
        request = self.factory.get("/home")
        request.garnett_language = "fr"
        request.session = {}
        self.middleware(request)
        self.assertIn("GARNETT_LANGUAGE_CODE", request.session)
        self.assertEqual(request.session["GARNETT_LANGUAGE_CODE"], "fr")

    def test_cache_middleware_fails_safely(self):
        """Test that the cache middleware still returns response if no session"""
        response = self.middleware(self.factory.get("/home"))
        self.assertEqual(response.content, b"Nice")
