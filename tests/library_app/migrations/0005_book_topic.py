# Generated by Django 3.1.13 on 2021-11-18 16:24

from django.db import migrations, models
import functools
import garnett.fields
import library_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0004_auto_20211103_0322'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='topic',
            field=garnett.fields.TranslatedField(models.CharField(default='', max_length=250), default=functools.partial(garnett.fields.translatable_default, *('',), **{}), fallback=library_app.models.BilingualTranslatedStr, help_text='A topic for a book. These are only shown in English and French to demonstrate how Bilingual support is possible'),
        ),
    ]
