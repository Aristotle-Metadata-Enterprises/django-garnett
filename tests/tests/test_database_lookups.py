from django.db import connection
from django.db.models.functions import Lower
from django.test import TestCase
from garnett.expressions import L
from garnett.patch import apply_patches, revert_patches

from unittest import skipIf, skipUnless

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

    @skipIf(connection.vendor == "mysql", "MariaDB uses case insensitive matching here")
    def test_exact(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(
                books.filter(title__en=self.book_data["title"]["en"]).exists()
            )
            self.assertTrue(books.filter(title=self.book_data["title"]["en"]).exists())
            self.assertFalse(books.filter(title=self.book_data["title"]["de"]).exists())
            # An inexact match won't be returned as true
            self.assertFalse(
                books.filter(title=self.book_data["title"]["en"].upper()).exists()
            )
            self.assertFalse(books.filter(title="A GOoD bOoK").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title=self.book_data["title"]["en"]).exists())
            self.assertTrue(books.filter(title=self.book_data["title"]["de"]).exists())

    @skipUnless(connection.vendor == "mysql", "Provide some coverage for MariaDB")
    def test_exact_mysql(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title=self.book_data["title"]["en"]).exists())
            self.assertFalse(books.filter(title=self.book_data["title"]["de"]).exists())
            # An inexact match shouldn't be returned as true, but is
            # We have this test so if this changes we will know.
            self.assertTrue(
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

    @skipUnless(connection.vendor == "sqlite", "Provide some coverage for SQLite")
    def test_contains_sqlite(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__contains="good").exists())
            self.assertFalse(books.filter(title__contains="gut").exists())
            # An inexact match shouldn't be returned
            # But it is. This isn't a deal breaker right now :/
            # We have this test so if this changes we will know.
            self.assertTrue(books.filter(title__contains="GOOD").exists())
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
            self.assertFalse(books.filter(title__endswith="BOOK").exists())
            self.assertFalse(books.filter(title__endswith="buch").exists())

        with set_field_language("de"):
            self.assertFalse(books.filter(title__endswith="book").exists())
            self.assertTrue(books.filter(title__endswith="buch").exists())
            self.assertFalse(books.filter(title__endswith="BUCH").exists())

    def test_iendswith(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertTrue(books.filter(title__iendswith="book").exists())
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
        # noqa: E731
        books = Book.objects.all()
        for lookup in [
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
            if lookup.startswith("i"):
                case_sensitive = False
                en_str = en_str.upper()
                de_str = de_str.upper()
            if "starts" in lookup or "contains" in lookup:
                en_str = en_str[0:-2]
                de_str = de_str[0:-2]
            if "end" in lookup or "contains" in lookup:
                en_str = en_str[2:]
                de_str = de_str[2:]

            try:
                with set_field_language("en"):
                    self.assertFalse(
                        books.filter(**{f"title__en__{lookup}": de_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__en__{lookup}": en_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__de__{lookup}": de_str}).exists()
                    )

                    # TODO: This test fails - maybe an issue with JSON contains in SQLite?
                    from django.db import connection

                    if case_sensitive and connection.vendor != "sqlite":
                        self.assertFalse(
                            books.filter(
                                **{f"title__en__{lookup}": en_str.upper()}
                            ).exists()
                        )
                        self.assertFalse(
                            books.filter(
                                **{f"title__de__{lookup}": de_str.upper()}
                            ).exists()
                        )

                with set_field_language("de"):
                    self.assertFalse(
                        books.filter(**{f"title__en__{lookup}": de_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__en__{lookup}": en_str}).exists()
                    )
                    self.assertTrue(
                        books.filter(**{f"title__de__{lookup}": de_str}).exists()
                    )
            except:  # noqa: E722 , pragma: no cover
                print(f"failed on {lookup} -- '{en_str}', '{de_str}'")
                raise

    @skipIf(connection.vendor == "mysql", "MariaDB has issues with JSON F lookups")
    def test_f_lookup(self):
        from garnett.expressions import LangF as F
        from django.db.models.functions import Upper

        self.book_data = dict(
            title={
                "en": "Mr. Bob Bobbertson",
                "de": "Herr Bob Bobbertson",
            },
            author="Mr. Bob Bobbertson",
            description="Mr. Bob Bobbertson's amazing self-titled autobiography",
            category={
                "dewey": 222,
                "subject": "Mr. Bob Bobbertson",
            },
            number_of_pages=100,
        )
        Book.objects.create(**self.book_data)

        books = Book.objects.all()

        self.assertTrue(  # Author match
            books.filter(description__istartswith=F("author")).exists()
        )

        with set_field_language("en"):
            annotated = books.annotate(en_title=F("title"))[0]
            self.assertEqual(annotated.title, annotated.en_title)
            annotated = books.annotate(en_title=F("title__xyz"))[0]
            self.assertEqual(annotated.en_title, None)

            self.assertTrue(  # Author=Title match
                books.filter(author=F("title")).exists()
            )

            self.assertTrue(  # Title=Author match
                books.filter(title__en__iexact=F("author")).exists()
            )
            self.assertTrue(  # Title=Author match
                books.filter(title__exact=F("author")).exists()
            )
            self.assertTrue(  # Title=Author match
                books.filter(title=F("author")).exists()
            )
            self.assertFalse(  # Title=Author match
                books.filter(title=Upper(F("author"))).exists()
            )
            self.assertTrue(  # Title=Author match
                books.filter(title__en__iexact=F("author")).exists()
            )
            self.assertTrue(  # Title=Author match
                books.filter(title__en__exact=F("author")).exists()
            )
            self.assertTrue(  # Description matches Author
                books.filter(description__istartswith=F("author")).exists()
            )
            self.assertTrue(  # Description en matches Author
                books.filter(description__en__istartswith=F("author")).exists()
            )
            self.assertTrue(  # Description starts with Title
                books.filter(description__istartswith=F("title")).exists()
            )

    @skipIf(connection.vendor == "mysql", "MariaDB has issues with JSON F lookups")
    # Should skip this if it is before Django 3.2 as support for text transforms was
    # added in Django 3.2
    def test_text_transform_f_lookup(self):
        """Test F lookups involving a text transform"""

        from django.db.models.functions import Lower, Upper
        from garnett.fields import TranslatedField
        from garnett.expressions import LangF as F

        Book.objects.all().delete()
        book_data = dict(
            title={
                "en": "A GOOD BOOK",
                "de": "EIN GUTES BUCH",
            },
            author="a good book",
            description="A book on how to be good, and stuff",
            category={"dewey": 222},
            number_of_pages=100,
        )
        Book.objects.create(**book_data)

        TranslatedField.register_lookup(Lower)
        TranslatedField.register_lookup(Upper)

        # Set the field language to english
        with set_field_language("en"):
            books = Book.objects.annotate(lower_title_exp=F("title__lower"))

            self.assertEqual(books.values()[0]['lower_title_exp'], Book.objects.first().title.lower())


class TestValuesList(TestCase):
    @set_field_language("en")
    def setUp(self):
        apply_patches()

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

    def tearDown(self):
        revert_patches()

    def test_values(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertEqual("A good book", books.values("title__en")[0]["title__en"])
            self.assertEqual("A good book", books.values("title")[0]["title"])

        with set_field_language("de"):
            self.assertEqual("Eine gut buch", books.values("title")[0]["title"])
            self.assertEqual("Eine gut buch", books.values("title")[0]["title"])
            self.assertEqual("A good book", books.values("title__en")[0]["title__en"])

    def test_values_list(self):
        books = Book.objects.all()
        with set_field_language("en"):
            self.assertEqual(
                "A good book", books.values_list("title__en", flat=True)[0]
            )
            self.assertEqual("A good book", books.values_list("title", flat=True)[0])

        with set_field_language("de"):
            self.assertEqual("Eine gut buch", books.values("title")[0]["title"])
            self.assertEqual("Eine gut buch", books.values_list("title", flat=True)[0])
            self.assertEqual(
                "A good book", books.values_list("title__en", flat=True)[0]
            )


class TestExpressions(TestCase):
    """Test queries using language lookup expression"""

    def setUp(self):
        with set_field_language("en"):
            self.book = Book.objects.create(
                title={
                    "en": "Testing for dummies",
                    "de": "Testen auf Dummies",
                },
                author="For dummies",
                description={
                    "en": "Testing but for dummies",
                    "de": "Testen aber für Dummies",
                },
                category={"cat": "book"},
                number_of_pages=2,
            )

    def test_order_by_translate_field(self):
        with set_field_language("en"):
            qs = Book.objects.order_by(L("title"))
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs[0].title, "Testing for dummies")

    def test_order_by_lower_translate_field(self):
        with set_field_language("en"):
            qs = Book.objects.order_by(Lower(L("title")))
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs[0].title, "Testing for dummies")

    def test_annotate_translate_field(self):
        with set_field_language("en"):
            qs = Book.objects.annotate(foo=L("title"))
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs[0].foo, "Testing for dummies")

    def test_annotate_lower_translate_field(self):
        with set_field_language("en"):
            qs = Book.objects.annotate(foo=Lower(L("title")))
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs[0].foo, "testing for dummies")


@skipIf(connection.vendor == "sqlite", "JSONField contains isn't available on sqlite")
class TestJSONFieldLookups(TestCase):
    """Tests to ensure we are not messing with json field functionality"""

    def setUp(self):
        with set_field_language("en"):
            self.book = Book.objects.create(
                title="book",
                author="Book guy",
                description="cool book",
                category={
                    "data": {
                        "is": "nested",
                    }
                },
                number_of_pages=1000,
            )

    def test_root_contains(self):
        qs = Book.objects.filter(category__contains={"data": {"is": "nested"}})
        self.assertCountEqual(qs, [self.book])

    def test_sub_contains(self):
        qs = Book.objects.filter(category__data__contains={"is": "nested"})
        self.assertCountEqual(qs, [self.book])
