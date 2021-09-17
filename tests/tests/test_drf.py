from django.test import TestCase, override_settings
from library_app.models import Book
from garnett.context import set_field_language

from library_app.api.serializers import BookSerializer


@override_settings(GARNETT_TRANSLATABLE_LANGUAGES=["en", "fr", "de"])
class TestSerializer(TestCase):
    """Test different language locales work"""

    def setUp(self):
        self.titles = {
            "en": "Hello",
            "fr": "Bonjour",
            "de": "Guten Tag",
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

    def test_read_serializer(self):
        obj = BookSerializer().to_representation(self.book)
        self.assertEqual(obj["title"], "Hello")

        with set_field_language("en"):
            self.assertEqual(self.book.title, "Hello")

        with set_field_language("fr"):
            self.assertEqual(self.book.title, "Bonjour")

        with set_field_language("de"):
            self.assertEqual(self.book.title, "Guten Tag")

    def test_write_serializer(self):
        obj = BookSerializer().to_representation(self.book)
        new_titles = {
            "en": "Bye",
            "fr": "Au revoir",
            "de": "Aufweidersen",
        }

        with set_field_language("en"):
            obj["title"] = new_titles
            new_obj = BookSerializer(data=obj)
            new_obj.is_valid()
            new_obj.update(self.book, new_obj.validated_data)

            self.assertEqual(self.book.title, "Bye")
            self.assertEqual(self.book.translations.title, new_titles)

        with set_field_language("fr"):
            obj["title"] = "Bonjour"
            new_obj = BookSerializer(data=obj)
            new_obj.is_valid()
            new_obj.update(self.book, new_obj.validated_data)

            self.assertEqual(self.book.title, "Bonjour")
            self.assertEqual(self.book.translations.title["en"], "Bye")
            self.assertEqual(self.book.translations.title["de"], "Aufweidersen")
