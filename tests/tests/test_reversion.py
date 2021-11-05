import json
from django.test import TestCase
import reversion
from garnett.serializers.json import Deserializer

from garnett.context import set_field_language
from library_app.models import Book

book_data = dict(
    title={
        "en": "A good book",
        "de": "Eine gut buch",
    },
    author="I. M. Nice",
    description="A book on how to be good, and stuff",
    category={"dewey": 222},
    number_of_pages=100,
)


class TestReversion(TestCase):
    def setUp(self):
        with set_field_language("en"), reversion.create_revision():
            self.book = Book(**book_data)
            self.book.save()

        # Need this to prevent data persisting across tests
        self.book = Book.objects.get(pk=self.book.pk)

    def test_reversion_numbers(self):
        num_versions_before = reversion.models.Version.objects.get_for_object(
            self.book
        ).count()
        with reversion.create_revision():
            new_title = {
                "en": "New title",
                "de": "Neuer titel",
            }
            with set_field_language("en"):
                self.book.title = new_title["en"]
            with set_field_language("de"):
                self.book.title = new_title["de"]

            self.book.save()
            self.book.refresh_from_db()

        num_versions_after = reversion.models.Version.objects.get_for_object(
            self.book
        ).count()
        self.assertEqual(num_versions_after, num_versions_before + 1)

    def test_reversion_content(self):
        version_before = reversion.models.Version.objects.get_for_object(
            self.book
        ).first()
        deserialised = list(Deserializer(version_before.serialized_data))[0].object
        self.assertEqual(deserialised.title_tsall, book_data["title"])

        with reversion.create_revision():
            new_title = {
                "en": "New title",
                "de": "Neuer titel",
            }
            with set_field_language("en"):
                self.book.title = new_title["en"]
            with set_field_language("de"):
                self.book.title = new_title["de"]

            self.book.save()
            self.book.refresh_from_db()

        version_after = reversion.models.Version.objects.get_for_object(
            self.book
        ).first()
        deserialised = list(Deserializer(version_after.serialized_data))[0].object
        self.assertEqual(deserialised.title_tsall, new_title)
