from django.test import TestCase, override_settings


from library_app.models import Book
from garnett.fields import next_language_fallback, translation_fallback
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

        result = next_language_fallback(self.title, self.book)
        self.assertEqual(result, "Das Buch")
        self.assertTrue(result.is_fallback)
        self.assertEqual(result.fallback_language, "de")

    def test_next_language_fallback_none(self):
        """Test next language fallback when none present"""
        self.book.title = {}
        self.book.save()

        result = next_language_fallback(self.title, self.book)
        self.assertEqual(result, "")
        self.assertTrue(result.is_fallback)
        self.assertEqual(result.fallback_language, "")

    def test_default_fallback(self):
        self.book.title = {"de": "Das Buch", "fr": "Le livre"}
        self.book.save()

        result = translation_fallback(self.title, self.book)
        self.assertEqual(
            result, "No translation of title available in English [English]."
        )
