from django.db import models
from django.test import TestCase

from garnett.expressions import L, LangF
from garnett.context import set_field_language
from garnett.fields import TranslatedField
from library_app.models import Book, RANDOM_STR, BLEACH_STR

book_data = dict(
    title={
        "en": "A good book",
        "de": "Eine gut buch",
    },
    author="I. M. Nice",
    description={
        "en": "A book on how to be good, and stuff",
        "fr": "Un livre sur la façon d'être bon, et tout"
    },
    category={"dewey": 222},
    number_of_pages=100,
)


class TestModelChanges(TestCase):
    def setUp(self):
        with set_field_language("en"):
            self.book = Book(**book_data)
            self.book.save()

        # Need this to prevent data persisting across tests
        self.book = Book.objects.get(pk=self.book.pk)

    def test_available_languages(self):
        self.assertEqual(
            sorted([l.to_tag() for l in self.book.available_languages]),
            ["de", "en", "fr"]
        )


class TestQuerySet(TestCase):
    def setUp(self):
        with set_field_language("en"):
            self.book = Book(**book_data)
            self.book.save()

        # Need this to prevent data persisting across tests
        self.book = Book.objects.get(pk=self.book.pk)

    def test_values(self):
        with set_field_language("en"):
            titles = list(Book.objects.all().values(L('title')))
            self.assertEqual(titles, [{'title': book_data['title']['en']}])
        with set_field_language("de"):
            titles = list(Book.objects.all().values(L('title')))
            self.assertEqual(titles, [{'title': book_data['title']['de']}])
