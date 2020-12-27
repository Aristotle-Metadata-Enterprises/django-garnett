from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from garnett import fields
from garnett.utils import get_current_language


def validate_length(value):
    if len(value) > 50:
        raise ValidationError(
            _('Title is too long')
        )


def title_fallback(field, obj):
    current_lang = get_current_language()
    if obj.translations.title.items():
        lang, value = list(obj.translations.title.items())[0]
        return f"{value} (Book title unavailable in {current_lang}, falling back to {lang})"
    else:
        return "No translations available for this book"


class Book(models.Model):
    number_of_pages = models.PositiveIntegerField()
    title = fields.TranslatedCharField(
        fallback=title_fallback,
        validators=[validate_length]
    )
    author = models.TextField()
    description = fields.TranslatedTextField()
    category = models.JSONField()

    def get_absolute_url(self):
        return f"/book/{self.pk}"

    def __str__(self):
        return self.title
