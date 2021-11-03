from django.test import TestCase
from django.urls import reverse
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


class BookFormTestBase:
    url_name = "update_book"

    def setUp(self):
        with set_field_language("en"):
            self.book = Book.objects.create(**book_data)

    def test_book_updates(self):
        new_title = "A better book"
        data = book_data.copy()
        data["title"] = new_title
        response = self.client.post(
            reverse(self.url_name, args=[self.book.pk]) + "?glang=en",
            data=data,
        )

        self.book.refresh_from_db()

        with set_field_language("en"):
            self.assertTrue(self.book.title, new_title)
            self.assertTrue(self.book.description, data["description"])
        with set_field_language("de"):
            self.assertTrue(self.book.title, book_data["title"]["de"])

    def test_book_updates_in_german(self):
        new_title = "Das better book"
        data = book_data.copy()
        data["title"] = new_title
        data["description"] = "Ist gud"
        response = self.client.post(
            reverse(self.url_name, args=[self.book.pk]) + "?glang=de",
            data=data,
        )

        self.book.refresh_from_db()

        with set_field_language("de"):
            self.assertTrue(self.book.title, new_title)
            self.assertTrue(self.book.description, data["description"])
        with set_field_language("de"):
            # Test to ensure that the English title hasn't changed
            self.assertTrue(self.book.title, book_data["title"]["en"])
            self.assertTrue(self.book.description, book_data["description"])


class BookFormTests(BookFormTestBase, TestCase):
    url_name = "update_book"
