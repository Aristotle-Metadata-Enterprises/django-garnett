from django.apps import apps
from django.test import TestCase
import json

from library_app.models import Book
from garnett.context import set_field_language
from garnett.migrate import get_migration
from garnett.utils import get_current_language_code


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

    def test_author_reverse_migration(self):
        """Test migrating data in author back to original state"""
        lang = get_current_language_code()
        self.nice.author = json.dumps({lang: self.nice.author})
        self.nice.save()
        self.bad.author = json.dumps({lang: self.bad.author})
        self.bad.save()

        migration = get_migration("library_app", {"book": ["author"]})
        # Call backward migration directly with current apps
        migration.reverse_code(apps, None)

        self.nice.refresh_from_db()
        self.assertEqual(self.nice.author, "Nice")
        self.bad.refresh_from_db()
        self.assertEqual(self.bad.author, "Bad")

    def test_reverse_fails_if_wrong_langauge(self):
        """Test that reversing migration in a different language fails"""
        with set_field_language("en"):
            self.nice.author = json.dumps({"en": self.nice.author})
            self.nice.save()
            self.bad.author = json.dumps({"en": self.bad.author})
            self.bad.save()

        migration = get_migration("library_app", {"book": ["author"]})
        with set_field_language("de"):
            with self.assertRaises(KeyError):
                migration.reverse_code(apps, None)
