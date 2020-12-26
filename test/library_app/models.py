from django.db import models
from garnett import fields
from garnett.utils import get_current_language


def title_fallback(field, obj):
    current_lang = get_current_language()
    if obj.translations.title.items():
        lang, value = list(obj.translations.title.items())[0]
        return f"{value} (Book title unavailable in {current_lang}, falling back to {lang})"
    else:
        return "No translations available for this book"


class Book(models.Model):
    number_of_pages = models.PositiveIntegerField()
    title = fields.TranslatedCharField(fallback=title_fallback)
    author = models.TextField()
    description = fields.TranslatedTextField()
    category = models.JSONField()

    def get_absolute_url(self):
        return f"/book/{self.pk}"

    def __str__(self):
        return self.title
