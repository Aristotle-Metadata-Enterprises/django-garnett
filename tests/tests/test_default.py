from django.test import TestCase

from garnett.context import set_field_language
from library_app.models import DefaultBook


class DefaultTestCase(TestCase):
    """Test setting of default on translated field"""

    def test_default(self):
        """Test that default is returned by getter"""
        book = DefaultBook.objects.create(number_of_pages=100)
        self.assertEqual(book.title, "DEFAULT TITLE")

    def test_language_default(self):
        """Test that default creates dict using current language"""
        with set_field_language("fr"):
            book = DefaultBook.objects.create(number_of_pages=100)
            self.assertEqual(book.title, "DEFAULT TITLE")
            self.assertEqual(book.title_tsall, {"fr": "DEFAULT TITLE"})

    def test_default_function(self):
        """Test that default is returned by getter when inner default is function"""
        book = DefaultBook.objects.create(number_of_pages=100)
        self.assertEqual(book.author, "John Jimson")

    def test_language_default_function(self):
        """Test that dict is correct when inner default is function"""
        with set_field_language("fr"):
            book = DefaultBook.objects.create(number_of_pages=100)
            self.assertEqual(book.author, "John Jimson")
            self.assertEqual(book.author_tsall, {"fr": "John Jimson"})

    def test_default_deconstruct(self):
        """Make sure default callable is serialized properly"""
        title = DefaultBook._meta.get_field("title")
        kwargs = title.deconstruct()[3]
        self.assertIn("default", kwargs)
        self.assertTrue(callable(kwargs["default"]))

    def test_default_empty_string(self):
        """Test default works when empty string"""
        book = DefaultBook(number_of_pages=100)
        self.assertEqual(book.description, "")
