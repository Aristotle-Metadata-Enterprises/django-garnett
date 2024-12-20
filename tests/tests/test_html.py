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
        "fr": "Un livre sur la façon d'être bon, et tout",
    },
    category={"dewey": 222},
    number_of_pages=100,
)


class TestHTMLRender(TestCase):
    def setUp(self):
        with set_field_language("en"):
            self.book = Book(**book_data)
            self.book.save()

        # Need this to prevent data persisting across tests
        self.book = Book.objects.get(pk=self.book.pk)

    def test_field_html_render(self):
        with set_field_language("en"):
            self.assertTrue(
                "[en]" not in self.book.title.__html__()
            )
            self.assertEqual(self.book.title.__html__(), self.book.title)

        with set_field_language("de"):
            self.assertTrue(
                "[de]" not in self.book.title.__html__()
            )
            self.assertEqual(self.book.title.__html__(), self.book.title)

        with set_field_language("fr"):
            tag = self.book.title.fallback_language.to_tag()
            self.assertTrue(
                f"[{tag}]" in self.book.title.__html__()
            )
            self.assertTrue(self.book.title_tsall[tag] in self.book.title.__html__())
