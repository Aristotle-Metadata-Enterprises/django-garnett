from django.db import connection
from django.test import TestCase

from unittest import skipUnless

from garnett.context import set_field_language
from garnett.lookups import LangTrigramSimilarity
from library_app.models import Book

from django.contrib.postgres.search import TrigramSimilarity


def similar_qs(qs, field, text):
    return qs.annotate(similarity=TrigramSimilarity(field, text))


def lang_similar_qs(qs, field, text):
    return qs.annotate(similarity=LangTrigramSimilarity(field, text))


@skipUnless(connection.vendor == "postgresql", "Search only works on Postgres")
class TestPGSearchLookups(TestCase):
    @set_field_language("en")
    def setUp(self):
        self.book_data = dict(
            title={
                "en": "A good book",
                "de": "Eine gut buch",
                "sjn": "A man parv",
            },
            author="I. M. Nice",
            description="A book on how to be good, and stuff",
            category={"dewey": 222},
            number_of_pages=100,
        )
        Book.objects.create(**self.book_data)

    def test_search(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__search="book").exists())
            self.assertFalse(books.filter(title__search="buch").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__search="book").exists())
            self.assertTrue(books.filter(title__search="buch").exists())

    def test_trigram(self):
        books = Book.objects.all()

        # Testing a regular field to make sure trigrams are enabled
        similar = similar_qs(books, "author", "I. R. Mice")
        self.assertTrue(similar.filter(similarity__gt=0.3).exists())
        self.assertTrue(books.filter(author__trigram_similar="nice").exists())

        # Testing a translation field to make sure trigrams work
        with set_field_language("en"):
            self.assertTrue(books.filter(title__trigram_similar="bood").exists())
            self.assertFalse(books.filter(title__trigram_similar="buck").exists())
            self.assertFalse(books.filter(title__trigram_similar="ein").exists())

            self.assertTrue(lang_similar_qs(books, "title", "bood").exists())
            # We can't get this to 0 because there is some overlap between German and English
            self.assertTrue(
                0.2 > lang_similar_qs(books, "title", "ein gut buck").first().similarity
            )

        with set_field_language("de"):
            self.assertFalse(books.filter(title__trigram_similar="bood").exists())
            self.assertTrue(books.filter(title__icontains="buch").exists())
            self.assertTrue(books.filter(title__trigram_similar="ein buck").exists())
            self.assertTrue(books.filter(title__trigram_similar="eime buch").exists())

    def test_trigram_similarity(self):
        books = Book.objects.all()
        with set_field_language("en"):
            en_similarity = (
                lang_similar_qs(books, "title", "eine gut buck").first().similarity
            )
        with set_field_language("de"):
            de_similarity = (
                lang_similar_qs(books, "title", "eine gut buck").first().similarity
            )

        self.assertTrue(de_similarity > en_similarity)
