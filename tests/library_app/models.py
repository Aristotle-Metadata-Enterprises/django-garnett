from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from garnett import fields
from garnett.utils import get_current_language_code


def validate_length(value):
    if len(value) < 3:
        raise ValidationError(_("Title is too short"))


def title_fallback(context):
    current_lang = get_current_language_code()
    if context.items():
        lang, value = list(context.items())[0]
        return (
            lang,
            f"{value} (Book title unavailable in {current_lang}, falling back to {lang})",
        )
    else:
        return None, "No translations available for this book"


class Book(models.Model):
    number_of_pages = models.PositiveIntegerField()
    title = fields.Translated(
        models.CharField(max_length=250, validators=[validate_length]),
        fallback=title_fallback,
        help_text=_("The name for a book. (Multilingal field)")
    )
    author = models.TextField(
        help_text=_("The name of the person who wrote the book (Single language field)")
    )
    description = fields.Translated(
        models.TextField(
            help_text=_("Short details about a book. (Multilingal field)")
        ))
    category = models.JSONField()

    def get_absolute_url(self):
        return f"/book/{self.pk}"

    def __str__(self):
        return self.title


def default_author():
    return "John Jimson"


class DefaultBook(models.Model):
    """A model used to test default on inner fields"""

    number_of_pages = models.PositiveIntegerField()
    title = fields.Translated(models.CharField(blank=True, default="DEFAULT TITLE"))
    author = fields.Translated(models.CharField(blank=True, default=default_author))
    description = fields.Translated(models.CharField(blank=True, default=""))
