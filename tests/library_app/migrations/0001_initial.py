# Generated by Django 3.1.13 on 2022-01-11 10:10

from django.db import migrations, models
from django.contrib.postgres.operations import TrigramExtension
import functools
import garnett.fields
import library_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number_of_pages", models.PositiveIntegerField()),
                (
                    "title",
                    models.CharField(
                        max_length=250,
                        validators=[library_app.models.validate_length],
                        help_text="The name for a book. (Multilingal field)",
                    ),
                ),
                (
                    "author",
                    models.TextField(
                        default="Anon",
                        help_text="The name of the person who wrote the book (Single language field)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Short details about a book. (Multilingal field)",
                    ),
                ),
                ("category", models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="DefaultBook",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number_of_pages", models.PositiveIntegerField()),
                (
                    "title",
                    garnett.fields.TranslatedField(
                        models.CharField(blank=True, default="DEFAULT TITLE"),
                        default=functools.partial(
                            garnett.fields.translatable_default,
                            *("DEFAULT TITLE",),
                            **{}
                        ),
                        fallback=None,
                    ),
                ),
                (
                    "author",
                    garnett.fields.TranslatedField(
                        models.CharField(
                            blank=True, default=library_app.models.default_author
                        ),
                        default=functools.partial(
                            garnett.fields.translatable_default,
                            *(library_app.models.default_author,),
                            **{}
                        ),
                        fallback=None,
                    ),
                ),
                (
                    "description",
                    garnett.fields.TranslatedField(
                        models.CharField(blank=True, default=""),
                        default=functools.partial(
                            garnett.fields.translatable_default, *("",), **{}
                        ),
                        fallback=None,
                    ),
                ),
            ],
        ),
        TrigramExtension(),
    ]
