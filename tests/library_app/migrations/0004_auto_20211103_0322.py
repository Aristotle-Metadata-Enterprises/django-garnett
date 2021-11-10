# Generated by Django 3.1.13 on 2021-11-03 03:22

from django.db import migrations, models
import garnett.fields
import library_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0003_defaultbook'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.TextField(default='Anon', help_text='The name of the person who wrote the book (Single language field)'),
        ),
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=garnett.fields.TranslatedField(models.TextField(help_text='Short details about a book. (Multilingal field)'), fallback=None, help_text='Short details about a book. (Multilingal field)'),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=garnett.fields.TranslatedField(models.CharField(max_length=250, validators=[library_app.models.validate_length]), fallback=library_app.models.TitleTranslatedStr, help_text='The name for a book. (Multilingal field)'),
        ),
    ]
