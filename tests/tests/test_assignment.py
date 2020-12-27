from django.db import connection
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


class TestFieldAssignment(TestCase):
    @set_field_language("en")
    def setUp(self):
        self.book_data = book_data.copy()
        Book.objects.create(**self.book_data)

    def test_assignment(self):
        en_new_title = "New title"
        de_new_title = "Neuer titel"
        book = Book.objects.first()
        with set_field_language("en"):
            book.title = en_new_title
        with set_field_language("de"):
            book.title = "Neuer titel"

        book.save()
        book.refresh_from_db()

        with set_field_language("en"):
            self.assertEqual(book.title, en_new_title)
            self.assertNotEqual(book.title, de_new_title)
        with set_field_language("de"):
            self.assertEqual(book.title, de_new_title)
            self.assertNotEqual(book.title, en_new_title)

        self.assertEqual(
            book.translations.title,
            {
                "en": en_new_title,
                "de": de_new_title,
            },
        )


class TestQuerysetAssignment(TestCase):
    def test_qs_create_from_dict(self):
        book = Book.objects.create(**book_data)
        self.assertEqual(book.translations.title, book_data["title"])
        self.assertNotEqual(book.translations.description, book_data["description"])
        self.assertEqual(
            book.translations.description, {"en": book_data["description"]}
        )
        with set_field_language("en"):
            self.assertEqual(book.title, book_data["title"]["en"])
            self.assertEqual(book.description, book_data["description"])

    def test_qs_create_from_strings(self):
        book_data = dict(
            title="A good book",
            author="I. M. Nice",
            description="A book on how to be good, and stuff",
            category={"dewey": 222},
            number_of_pages=100,
        )
        book = Book.objects.create(**book_data)
        self.assertNotEqual(book.translations.title, book_data["title"])
        self.assertNotEqual(book.translations.description, book_data["description"])
        self.assertEqual(book.translations.title, {"en": book_data["title"]})
        self.assertEqual(
            book.translations.description, {"en": book_data["description"]}
        )
        with set_field_language("en"):
            self.assertEqual(book.title, book_data["title"])
            self.assertEqual(book.description, book_data["description"])

    def test_qs_bulk_create_from_dict(self):
        Book.objects.bulk_create([Book(**book_data)])
        book = Book.objects.first()
        self.assertEqual(book.translations.title, book_data["title"])
        self.assertNotEqual(book.translations.description, book_data["description"])
        self.assertEqual(
            book.translations.description, {"en": book_data["description"]}
        )
        with set_field_language("en"):
            self.assertEqual(book.title, book_data["title"]["en"])
            self.assertEqual(book.description, book_data["description"])

    def test_qs_bulk_create_from_strings(self):
        book_data = dict(
            title="A good book",
            author="I. M. Nice",
            description="A book on how to be good, and stuff",
            category={"dewey": 222},
            number_of_pages=100,
        )
        Book.objects.bulk_create([Book(**book_data)])
        book = Book.objects.first()
        self.assertNotEqual(book.translations.title, book_data["title"])
        self.assertNotEqual(book.translations.description, book_data["description"])
        self.assertEqual(book.translations.title, {"en": book_data["title"]})
        self.assertEqual(
            book.translations.description, {"en": book_data["description"]}
        )
        with set_field_language("en"):
            self.assertEqual(book.title, book_data["title"])
            self.assertEqual(book.description, book_data["description"])


class TestContext(TestCase):
    def test_nesting_context(self):
        with set_field_language("de"):
            book = Book.objects.create(**book_data.copy())
            with set_field_language("en"):
                with set_field_language("de"):
                    book.title = "de-title"
                    with set_field_language("en"):
                        book.description = "en-description"
                    book.description = "de-description"
                book.title = "en-title"

        self.assertEqual(book.translations.title, {"en": "en-title", "de": "de-title"})
        self.assertEqual(
            book.translations.description,
            {"en": "en-description", "de": "de-description"},
        )
        book.save()
        book.refresh_from_db()
        self.assertEqual(book.translations.title, {"en": "en-title", "de": "de-title"})
        self.assertEqual(
            book.translations.description,
            {"en": "en-description", "de": "de-description"},
        )
