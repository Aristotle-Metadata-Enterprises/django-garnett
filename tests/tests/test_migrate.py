from django.apps import apps
from django.test import TestCase
import json

from library_app.models import Book
from garnett.context import set_field_language
from garnett.migrate import get_migration


class TestDataMigration(TestCase):
    def setUp(self):
        with set_field_language("en"):
            self.nice = Book.objects.create(
                title="Nice book",
                author="Nice",
                description="Nice",
                category={},
                number_of_pages=100,
            )
            self.bad = Book.objects.create(
                title="Bad book",
                author="Bad",
                description="Bad",
                category={},
                number_of_pages=100,
            )

    def test_author_migration(self):
        """Test migrating data in author to translated field json"""
        migration = get_migration("library_app", {"book": ["author"]})
        # Call forward migation function directly with current apps
        migration.code(apps, None)

        self.nice.refresh_from_db()
        self.assertEqual(json.loads(self.nice.author), {"en": "Nice"})
        self.bad.refresh_from_db()
        self.assertEqual(json.loads(self.bad.author), {"en": "Bad"})
