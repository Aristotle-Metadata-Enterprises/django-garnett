from django.test import TestCase

from garnett.context import set_field_language
from library_app.models import DefaultBook


class DefaultTestCase(TestCase):
    """Test setting of default on translated field"""

    def test_default(self):
        """Test that default works as if field is a CharField"""
        book = DefaultBook.objects.create(number_of_pages=100)

        self.assertEqual(book.title, "DEFAULT TITLE")

    def test_language_default(self):
        """Test that default creates dict using current language"""
        with set_field_language("fr"):
            book = DefaultBook.objects.create(number_of_pages=100)

            self.assertEqual(book.title, "DEFAULT TITLE")
            self.assertEqual(book.title_tsall, {"fr": "DEFAULT TITLE"})

    def test_default_deconstruct(self):
        """Make sure default callable is serialized properly"""
        title = DefaultBook._meta.get_field("title")
        kwargs = title.deconstruct()[3]
        self.assertIn("default", kwargs)
        self.assertTrue(callable(kwargs["default"]))
