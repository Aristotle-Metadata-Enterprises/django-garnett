from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from garnett import fields
from garnett.utils import get_current_language


def validate_length(value):
    if len(value) < 3:
        raise ValidationError(_("Title is too short"))


def title_fallback(field, obj):
    current_lang = get_current_language()
    if obj.translations.title.items():
        lang, value = list(obj.translations.title.items())[0]
        return f"{value} (Book title unavailable in {current_lang}, falling back to {lang})"
    else:
        return "No translations available for this book"


class Book(models.Model):
    number_of_pages = models.PositiveIntegerField()
    title = fields.Translated(
        models.CharField(max_length=250, validators=[validate_length]),
        fallback=title_fallback,
    )
    author = models.TextField()
    description = fields.Translated(models.TextField())
    category = models.JSONField()

    def get_absolute_url(self):
        return f"/book/{self.pk}"

    def __str__(self):
        return self.title
