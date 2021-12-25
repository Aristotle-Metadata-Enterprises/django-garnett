from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.http import urlencode
from library_app.models import Book
from garnett.context import set_field_language


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

    def test_filter(self):
        response = self.client.get(
            reverse("library_app_api:list_create_book")
            + "?"
            + urlencode({"title": self.titles["en"]}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.book.pk)

        response = self.client.get(
            reverse("library_app_api:list_create_book")
            + "?"
            + urlencode({"title": self.titles["fr"]}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.client.get(
            reverse("library_app_api:list_create_book")
            + "?"
            + urlencode({"title": self.titles["fr"], "glang": "fr"}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.book.pk)
