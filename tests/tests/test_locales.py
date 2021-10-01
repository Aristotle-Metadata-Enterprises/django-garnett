from django.test import TestCase, override_settings

from library_app.models import Book
from garnett.context import set_field_language
from garnett.utils import normalise_language_codes


@override_settings(GARNETT_TRANSLATABLE_LANGUAGES=["en", "en-AU", "en-US"])
class TestFallbacks(TestCase):
    """Test different language locales work"""

    def setUp(self):
        self.titles = {
            "en": "Hello friend!",
            "en-au": "G'Day mate!",
            "en-Us": "Howdy partner!",
        }
        with set_field_language("en"):
            self.book = Book.objects.create(
                title=self.titles,
                author="Some Guy",
                description="A book on saying hello",
                category={},
                number_of_pages=20,
            )

        self.title = Book._meta.get_field("title")

    def test_normalisation(self):
        self.assertEqual(
            self.book.translations.title, normalise_language_codes(self.titles)
        )

    def test_locale(self):
        with set_field_language("en"):
            self.assertTrue(self.book.title.startswith("Hello"))

        with set_field_language("en-US"):
            self.assertTrue(self.book.title.startswith("Howdy"))
            self.book.title = "Howdy pal!"
            self.book.save()

        with set_field_language("en-au"):
            self.assertTrue(self.book.title.startswith("G'Day"))

        self.assertEqual(
            self.book.translations.title,
            normalise_language_codes(
                {
                    "en": "Hello friend!",
                    "en-au": "G'Day mate!",
                    "en-Us": "Howdy pal!",
                }
            ),
        )
