# Generated by Django 3.1.14 on 2022-09-07 04:36

from django.db import migrations
import functools
import garnett.fields
import library_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0002_make_translatable'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='other_info',
            field=garnett.fields.TranslatedField(library_app.models.CustomTestingField(blank=True, default=''), default=functools.partial(garnett.fields.translatable_default, *('',), **{}), fallback=None),
        ),
    ]