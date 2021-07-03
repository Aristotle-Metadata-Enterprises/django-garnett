from django.test import TestCase
from django.db import connection
from django.db.models import F

from garnett.context import set_field_language
from unittest import skip
from library_app.models import SecureBook


class InverseTextTestCase(TestCase):
    """Test setting of default on translated field"""

    def setUp(self):
        with set_field_language("en"):
            self.book = SecureBook.objects.create(
                title={
                    "en": "A Good book - a story by Arthur Good",
                    "de": "Ein gutes Buch",
                },
                author="A Good",
            )

    def test_saves_reverse(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT title FROM library_app_securebook WHERE id=%s", [self.book.id]
            )
            row = cursor.fetchone()
            self.assertTrue("dooG" in row[0])
            self.assertTrue("Good" not in row[0])
        fetched_book = SecureBook.objects.filter(pk=self.book.pk).first()
        self.assertTrue(fetched_book is not None)
        self.assertTrue(fetched_book.title.startswith(fetched_book.author))

    def test_startswith(self):
        self.assertTrue(SecureBook.objects.all().count() == 1)
        with set_field_language("en"):
            fetched_book = SecureBook.objects.filter(title__icontains="dooG").first()
            self.assertTrue(fetched_book is None)
            fetched_book = SecureBook.objects.filter(
                title__icontains="A Good book"
            ).first()
            self.assertTrue(fetched_book is not None)
            self.assertTrue(fetched_book.pk == self.book.id)

    @skip("Impossible test")
    def test_f(self):
        """
        This test is included for completion - but is impossible.
        F(author) will do a direct match of the author column, which skips get_prep_value
        This means the author field won't be reversed, making matching impossible.
        """
        with set_field_language("en"):
            fetched_book = SecureBook.objects.filter(
                title__contains=F("author")
            ).first()
            self.assertTrue(fetched_book is not None)
            self.assertTrue(fetched_book.pk == self.book.id)
