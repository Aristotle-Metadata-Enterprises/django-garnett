from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

import garnett.exceptions
from garnett.context import set_field_language
from garnett.fields import TranslatedField
from library_app.models import Book, RANDOM_STR

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
        self.field = TranslatedField(models.TextField(), name="test_field")

    def test_validate_bad_code(self):
        """Test that validation prevents saving not selected code"""
        # Try to save in swedish
        with set_field_language("sv"), self.assertRaises(ValidationError):
            value = {"sv": "Swedish title"}
            self.field.clean(value, None)

    def test_validate_bad_json_value(self):
        """Make sure we can't save a non dict to the field"""
        value = 100

        with self.assertRaises(garnett.exceptions.LanguageStructureError):
            self.field.clean(value, None)

    def test_validate_bad_value_type(self):
        """Make sure tsall dict must be string to string"""
        value = {
            "en": 100,
            "fr": "good",
        }

        with set_field_language("en"), self.assertRaises(ValidationError) as err:
            # English language will fail
            self.field.clean(value, None)
            self.assertEqual(err.exception, 'Invalid value for language "en"')
        with set_field_language("fr"), self.assertRaises(ValidationError) as err:
            self.field.clean(value, None)
            self.assertEqual(err.exception, 'Invalid value for language "en"')

    def test_trigger_get_db_prep_save(self):
        content = "This is a book"
        Book.objects.create(
            title={
                "en": "A book",
                "de": "Eine Gut Buch",
            },
            author="No one",
            description="No description",
            category={"dewey": 123},
            number_of_pages=100,
            other_info=content,
        )
        # Expect only one object is created
        books = Book.objects.all()
        self.assertEqual(len(books), 1)

        # Expect CustomTestingField to be bleached
        book = books[0]
        self.assertEqual(book.other_info, content + RANDOM_STR)

        # Expect other fields will not be bleached
        self.assertNotIn(RANDOM_STR, book.title)
        self.assertNotIn(RANDOM_STR, book.author)
        self.assertNotIn(RANDOM_STR, book.description)
