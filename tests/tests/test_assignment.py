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


class TestFieldAssignment(TestCase):
    def setUp(self):
        with set_field_language("en"):
            self.book = Book.objects.create(**book_data)

        # Need this to prevent data persisting across tests
        self.book.refresh_from_db()

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

    def test_dict_assignment(self):
        data = {"en": "Stuff", "de": "Zeug"}
        with set_field_language("en"):
            self.book.title = data
            self.book.save()
            self.book.refresh_from_db()

            self.assertEqual(self.book.title, data["en"])

        with set_field_language("de"):
            self.assertEqual(self.book.title, data["de"])

    def test_max_length_validation(self):
        with set_field_language("en"):
            self.book.title = "A short value"
        with set_field_language("de"):
            self.book.title = "A long value " + ("=" * 350)
        with self.assertRaises(ValidationError):
            self.book.clean_fields()

    def test_validate_bad_code(self):
        """Test that validation prevents saving not selected code"""
        # Try to save in swedish
        with set_field_language("sv"):
            self.book.title = "Swedish title"

        with self.assertRaises(ValidationError):
            self.book.clean_fields()

    def test_setter_validate_wrong_type(self):
        with set_field_language("en"):
            with self.assertRaises(TypeError):
                self.book.title = 700

    def test_validate_bad_json_value(self):
        """Make sure we can't save a non dict to _tsall"""
        self.book.title_tsall = 100

        with self.assertRaises(ValidationError):
            self.book.clean_fields()

    def test_validate_bad_value_type(self):
        """Make sure tsall dict must be string to string"""
        self.book.title_tsall = {"en": 100}

        with self.assertRaises(ValidationError):
            self.book.clean_fields()


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
