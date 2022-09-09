from django.test import TestCase, override_settings

from library_app.models import Book
from garnett.translatedstr import VerboseTranslatedStr, NextTranslatedStr
from garnett.context import set_field_language


@override_settings(GARNETT_TRANSLATABLE_LANGUAGES=["en", "de", "fr"])
class TestFallbacks(TestCase):
    """Test fallback functions directly"""

    def setUp(self):
        with set_field_language("en"):
            self.book = Book.objects.create(
                title={"en": "The Book", "de": "Das Buch", "fr": "Le livre"},
                author="Some Guy",
                description="A nice book",
                category={"dewey": 222},
                number_of_pages=20,
            )

        self.title = Book._meta.get_field("title")

    def test_next_language_fallback(self):
        self.book.title = {"de": "Das Buch", "fr": "Le livre"}
        self.book.save()

        result = NextTranslatedStr(self.book.title_tsall)

        self.assertEqual(result, "Das Buch")
        self.assertTrue(result.is_fallback)
        self.assertEqual(result.fallback_language.to_tag(), "de")

    def test_next_language_fallback_none(self):
        """Test next language fallback when none present"""
        self.book.title = {}
        self.book.save()

        result = NextTranslatedStr(self.book.title_tsall)
        self.assertEqual(result, "")
        self.assertTrue(result.is_fallback)
        self.assertEqual(result.fallback_language, None)

    def test_default_fallback(self):
        self.book.title = {"de": "Das Buch", "fr": "Le livre"}
        self.book.save()

        result = VerboseTranslatedStr(self.book.title_tsall)
        self.assertEqual(
            result, "No translation of this field available in English [English]."
        )
