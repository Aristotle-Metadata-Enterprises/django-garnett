from django.test import TestCase

from garnett.context import set_field_language
from library_app.models import Book


class TestUpdates(TestCase):
    def setUp(self):
        with set_field_language("en"):
            self.book = Book.objects.create(
                title={
                    "en": "A good book",
                    "de": "Eine Gut Buch",
                },
                author="Someone",
                description="Its ok i guess",
                category={"dewey": 123},
                number_of_pages=100,
            )

    def test_update(self):
        """Test queryset .update on translated field with dict"""
        # Have to update with a dict instead of assigning a string with a language selected
        # as .update does a SQL UPDATE directly
        new_title = {"en": "New English Title", "de": "Eine Gut Buch"}
        Book.objects.filter(pk=self.book.pk).update(title=new_title)

        self.book.refresh_from_db()
        with set_field_language("en"):
            self.assertEqual(self.book.title, "New English Title")
            self.assertEqual(self.book.title_tsall, new_title)

    def test_bulk_update(self):
        """Test bulk_update on a translated field"""

        with set_field_language("en"):
            # Create second book
            book2 = Book.objects.create(
                title={
                    "en": "A bad book",
                    "de": "Eine Gut Buch",
                },
                author="Someone",
                description="Its not very good",
                category={"dewey": 123},
                number_of_pages=100,
            )

            self.assertEqual(Book.objects.count(), 2)
            # Bulk update title on the 2 books
            updated = []
            for book in Book.objects.all():
                book.title = "New English Title"
                updated.append(book)
            Book.objects.bulk_update(updated, ["title"])

            # Check that just the english title was updated
            self.book.refresh_from_db()
            self.assertEqual(
                self.book.title_tsall,
                {"en": "New English Title", "de": "Eine Gut Buch"},
            )

            book2.refresh_from_db()
            self.assertEqual(
                book2.title_tsall,
                {"en": "New English Title", "de": "Eine Gut Buch"},
            )
