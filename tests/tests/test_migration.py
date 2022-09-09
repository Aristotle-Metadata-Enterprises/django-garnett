import json
from django.apps import apps
from django.db import models
from django.test import TestCase

from garnett import migrate
from garnett.fields import TranslatedField
from garnett.context import set_field_language

from . import migration_test_utils


class TestMigrationHandlers(TestCase):
    def setUp(self):
        self.before_value = '{"not_real":"This is just some json someone hsa stored in a field - isn\'t that wierd?!"}'
        self.current_language = "en"
        self.after_value = {self.current_language: self.before_value}

    def test_1_and_2_forwards(self):
        step_1 = migrate.update_safe_encode_content_forwards(
            self.current_language, self.before_value
        )
        step_1 = json.loads(step_1)  # Mock loading back from the database
        step_2 = migrate.update_safe_prepare_translations_forwards(
            self.current_language, step_1
        )
        self.assertEqual(step_2, self.after_value)

    def test_1_and_2_backwards(self):
        step_1 = migrate.update_safe_prepare_translations_backwards(
            self.current_language, self.after_value
        )
        step_1 = json.dumps(step_1)  # Mock loading back from the database
        step_2 = migrate.update_safe_encode_content_backwards(
            self.current_language, step_1
        )
        self.assertEqual(step_2, self.before_value)

    def test_1_forwards_and_backwards(self):
        step_1 = migrate.update_safe_encode_content_forwards(
            self.current_language, self.before_value
        )
        step_2 = migrate.update_safe_encode_content_backwards(
            self.current_language, step_1
        )
        self.assertEqual(step_2, self.before_value)

    def test_2_backwards_and_forwards(self):
        step_1 = migrate.update_safe_prepare_translations_backwards(
            self.current_language, self.after_value
        )
        step_2 = migrate.update_safe_prepare_translations_forwards(
            self.current_language, step_1
        )
        self.assertEqual(step_2, self.after_value)


class TestDataMigration(migration_test_utils.MigrationsTestCase, TestCase):
    migrate_from = "0001_initial"
    migrate_to = "0002_make_translatable"
    app = "library_app"

    def setUpBeforeMigration(self, apps):
        Book = apps.get_model("library_app", "Book")
        self.title = "Before the migration, a string's story"
        self.description = "A moving tale of data was changed when going from place to place - but staying still!"
        self.book1 = Book.objects.create(
            title=self.title, description=self.description, number_of_pages=1
        )
        self.book1.refresh_from_db()

        # Make sure that the field we are reading is a regular CharField
        self.assertEqual(type(Book._meta.get_field("title")), models.CharField)
        self.assertEqual(self.book1.title, self.title)
        self.assertEqual(self.book1.description, self.description)

    def test_title_and_description(self):
        Book = apps.get_model("library_app", "Book")
        self.assertEqual(type(Book._meta.get_field("title")), TranslatedField)

        self.book1 = Book.objects.get(pk=self.book1.pk)

        self.assertEqual(self.book1.title_tsall, {"en": self.title})
        self.assertEqual(self.book1.description_tsall, {"en": self.description})

        with set_field_language("en"):
            self.assertEqual(self.book1.title, self.title)
            self.assertEqual(self.book1.description, self.description)
