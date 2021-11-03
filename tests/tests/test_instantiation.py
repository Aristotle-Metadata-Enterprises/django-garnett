from django.core.exceptions import ValidationError
from django.test import TestCase

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


class TestInstantiation(TestCase):
    def setUp(self):
        with set_field_language("en"):
            self.book = Book(**book_data)
            self.book.save()

        # Need this to prevent data persisting across tests
        self.book = Book.objects.get(pk=self.book.pk)

    def test_creation(self):
        with set_field_language("en"):
            self.assertEqual(self.book.title, book_data["title"]["en"])
            self.assertEqual(self.book.description, book_data["description"])
            self.assertEqual(self.book.author, book_data["author"])
            self.assertEqual(self.book.category, book_data["category"])
            self.assertEqual(self.book.number_of_pages, book_data["number_of_pages"])

    def test_assignment(self):
        en_new_title = "New title"
        de_new_title = "Neuer titel"
        with set_field_language("en"):
            self.book.title = en_new_title
        with set_field_language("de"):
            self.book.title = "Neuer titel"

        self.book.save()
        self.book.refresh_from_db()

        with set_field_language("en"):
            self.assertEqual(self.book.title, en_new_title)
            self.assertNotEqual(self.book.title, de_new_title)
        with set_field_language("de"):
            self.assertEqual(self.book.title, de_new_title)
            self.assertNotEqual(self.book.title, en_new_title)

        self.assertEqual(
            self.book.translations.title,
            {
                "en": en_new_title,
                "de": de_new_title,
            },
        )
