from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from garnett import fields
from garnett.translatedstr import TranslatedStr
from garnett.utils import get_languages, get_current_language


def validate_length(value):
    if len(value) < 3:
        raise ValidationError(_("Title is too short"))


class TitleTranslatedStr(TranslatedStr):
    """
    A translated string that includes a nice HTML styled fallback in django templates.
    """

    @classmethod
    def get_fallback_text(cls, content):
        if content.items():
            for lang in get_languages():
                if lang.to_tag() in content:
                    value = content[lang.to_tag()]
                    return (lang, f"{value}")
        else:
            return None, "No translations available for this book"

    def __html__(self) -> str:
        # Add leading [lang] wrapped in a span
        text = self
        if not self.is_fallback:
            return text
        elif not self.fallback_language:
            return "??"
        else:
            current_lang = get_current_language()
            lang = self.fallback_language
            return f"""
                <span class="fallback"
                data-lang-code="{lang.to_tag()}"
                title="Title unavailable in {current_lang.display_name()}, falling back to {lang.display_name()}"
                >
                <span class="fallback-lang-sq">[{lang.to_tag()}]</span>
                {self}
                </span>
            """


class Book(models.Model):
    number_of_pages = models.PositiveIntegerField()
    title = fields.Translated(
        models.CharField(max_length=250, validators=[validate_length]),
        fallback=TitleTranslatedStr,
        help_text=_("The name for a book. (Multilingal field)"),
    )
    author = models.TextField(
        help_text=_(
            "The name of the person who wrote the book (Single language field)"
        ),
        default="Anon",
    )
    description = fields.Translated(
        models.TextField(help_text=_("Short details about a book. (Multilingal field)"))
    )
    category = models.JSONField(blank=True, null=True)

    def get_absolute_url(self):
        return f"/book/{self.pk}"

    def __str__(self):
        return f"Book {self.title}"


def default_author():
    return "John Jimson"


class DefaultBook(models.Model):
    """A model used to test default on inner fields"""

    number_of_pages = models.PositiveIntegerField()
    title = fields.Translated(models.CharField(blank=True, default="DEFAULT TITLE"))
    author = fields.Translated(models.CharField(blank=True, default=default_author))
    description = fields.Translated(models.CharField(blank=True, default=""))
