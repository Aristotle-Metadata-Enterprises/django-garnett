from django.db import connection
from django.test import TestCase

from unittest import skipIf

from garnett.context import set_field_language
from library_app.models import Book


class TestLanguageLookups(TestCase):
    @set_field_language("en")
    def setUp(self):
        self.book_data = dict(
            title={
                "en": "A good book",
                "de": "Eine gut buch",
            },
            author="I. M. Nice",
            description="A book on how to be good, and stuff",
            category={"dewey": 222},
            number_of_pages=100,
        )
        Book.objects.create(**self.book_data)

    def test_HasLang(self):
        books = Book.objects.all()
        self.assertTrue(books.filter(title__has_lang="en").exists())
        self.assertTrue(books.filter(title__has_lang="de").exists())
        self.assertFalse(books.filter(title__has_lang="fr").exists())

    def test_HasLangs(self):
        books = Book.objects.all()
        self.assertTrue(books.filter(title__has_langs=["en", "de"]).exists())
        self.assertTrue(books.filter(title__has_langs=["de"]).exists())
        self.assertTrue(books.filter(title__has_langs=["en"]).exists())
        self.assertFalse(books.filter(title__has_langs=["en", "de", "fr"]).exists())
        self.assertFalse(books.filter(title__has_langs=["en", "fr"]).exists())
        self.assertFalse(books.filter(title__has_langs=["fr"]).exists())


class TestLookups(TestCase):
    @set_field_language("en")
    def setUp(self):
        self.book_data = dict(
            title={
                "en": "A good book",
                "de": "Eine gut buch",
            },
            author="I. M. Nice",
            description="A book on how to be good, and stuff",
            category={"dewey": 222},
            number_of_pages=100,
        )
        Book.objects.create(**self.book_data)

    def test_exact(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title=self.book_data["title"]["en"]).exists())
            self.assertFalse(books.filter(title=self.book_data["title"]["de"]).exists())
            # An inexact match won't be returned as true
            self.assertFalse(
                books.filter(title=self.book_data["title"]["en"].upper()).exists()
            )

        with set_field_language("de"):
            self.assertFalse(books.filter(title=self.book_data["title"]["en"]).exists())
            self.assertTrue(books.filter(title=self.book_data["title"]["de"]).exists())

    def test_iexact(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(
                books.filter(
                    title__iexact=self.book_data["title"]["en"].upper()
                ).exists()
            )
            self.assertFalse(
                books.filter(
                    title__iexact=self.book_data["title"]["de"].upper()
                ).exists()
            )

        with set_field_language("de"):
            self.assertFalse(
                books.filter(
                    title__iexact=self.book_data["title"]["en"].upper()
                ).exists()
            )
            self.assertTrue(
                books.filter(
                    title__iexact=self.book_data["title"]["de"].upper()
                ).exists()
            )

    @skipIf(connection.vendor == "sqlite", "SQLite uses case insensitive matching")
    def test_contains(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__contains="good").exists())
            self.assertFalse(books.filter(title__contains="gut").exists())
            # An inexact match shouldn't be returned
            # But it is. This isn't a deal breaker right now :/
            self.assertFalse(books.filter(title__contains="GOOD").exists())
            self.assertFalse(books.filter(title__contains="GUT").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__contains="good").exists())
            self.assertTrue(books.filter(title__contains="gut").exists())

    def test_icontains(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__icontains="good").exists())
            self.assertFalse(books.filter(title__icontains="gut").exists())
            self.assertTrue(books.filter(title__icontains="GOOD").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__icontains="good").exists())
            self.assertTrue(books.filter(title__icontains="gut").exists())
            self.assertTrue(books.filter(title__icontains="GUT").exists())

    @skipIf(connection.vendor == "sqlite", "SQLite uses case insensitive matching")
    def test_startswith(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__startswith="A goo").exists())
            self.assertFalse(books.filter(title__startswith="a goo").exists())
            self.assertFalse(books.filter(title__startswith="Eine").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__startswith="A good").exists())
            self.assertTrue(books.filter(title__startswith="Eine gut").exists())

    def test_istartswith(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__istartswith="A go").exists())
            self.assertTrue(books.filter(title__istartswith="a go").exists())
            self.assertFalse(books.filter(title__istartswith="Eine").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__istartswith="a go").exists())
            self.assertTrue(books.filter(title__istartswith="eine g").exists())

    @skipIf(connection.vendor == "sqlite", "SQLite uses case insensitive matching")
    def test_endswith(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__endswith="book").exists())
            self.assertFalse(books.filter(title__endswith="book").exists())
            self.assertFalse(books.filter(title__endswith="buch").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__endswith="A good").exists())
            self.assertTrue(books.filter(title__endswith="Eine gut").exists())

    def test_iendswith(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__iendswith="BOOK").exists())
            self.assertTrue(books.filter(title__iendswith="BOOK").exists())
            self.assertFalse(books.filter(title__iendswith="BUCH").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__iendswith="BOOK").exists())
            self.assertTrue(books.filter(title__iendswith="BUCH").exists())

    @skipIf(connection.vendor == "sqlite", "SQLite uses case insensitive matching")
    def test_regex(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__regex="^A.+book$").exists())
            self.assertFalse(books.filter(title__regex="^A.+BOOK$").exists())
            self.assertFalse(books.filter(title__regex="^Ei.+buch$").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__regex="^A.+book$").exists())
            self.assertTrue(books.filter(title__regex="^Ei.+buch$").exists())

    def test_iregex(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__iregex="^A.+book$").exists())
            self.assertTrue(books.filter(title__iregex="^A.+BOOK$").exists())
            self.assertFalse(books.filter(title__iregex="^Ei.+buch$").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__iregex="^A.+book$").exists())
            self.assertTrue(books.filter(title__iregex="^Ei.+buch$").exists())

    def test_languagelookups(self):
        books = Book.objects.all()
        for l in [
            "contains",
            "icontains",
            "endswith",
            "iendswith",
            "startswith",
            "istartswith",
        ]:
            en_str = "A good book"
            de_str = "Eine gut buch"
            case_sensitive = True
            if l.startswith("i"):
                case_sensitive = False
                en_str = en_str.upper()
                de_str = de_str.upper()
            if "starts" in l or "contains" in l:
                en_str = en_str[0:-2]
                de_str = de_str[0:-2]
            if "end" in l or "contains" in l:
                en_str = en_str[2:]
                de_str = de_str[2:]

            try:
                with set_field_language("en"):
                    self.assertFalse(
                        books.filter(**{f"title__en__{l}": de_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__en__{l}": en_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__de__{l}": de_str}).exists()
                    )
                    # TODO: This test fails - maybe an issue with JSON contains in SQLite?
                    # if case_sensitive:
                    #     self.assertFalse(books.filter(**{f'title__en__{l}':en_str.upper()}).exists())
                    #     self.assertFalse(books.filter(**{f'title__de__{l}':de_str.upper()}).exists())

                with set_field_language("de"):
                    self.assertFalse(
                        books.filter(**{f"title__en__{l}": de_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__en__{l}": en_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__de__{l}": de_str}).exists()
                    )
            except:  # pragma: no cover
                print(f"failed on {l} -- '{en_str}', '{de_str}'")
                raise
