from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from garnett import fields
from garnett.translatedstr import TranslatedStr
from garnett.utils import get_current_language_code, get_languages, get_current_language


def validate_length(value):
    if len(value) < 3:
        raise ValidationError(_("Title is too short"))


class TitleTranslatedStr(TranslatedStr):
    def get_fallback_text(content):
        current_lang = get_current_language_code()
        if content.items():
            for lang in get_languages():
                if lang.language in content:
                    # self.fallback_language = lang
                    value = content[lang.language]
                    return (lang, f"{value}")
        else:
            return None, "No translations available for this book"

    def __html__(self) -> str:
        # Add leading [lang] wrapped in a span
        text = self
        print(f"{self.is_fallback=}")
        print(self.fallback_language)
        print(type(self.fallback_language))
        if not self.is_fallback:
            return text
        elif not self.fallback_language:
            return "??"
        else:
            current_lang = get_current_language()
            lang = self.fallback_language
            return f"""
                <span class="fallback"
                data-lang-code="{lang.language}"
                title="Title unavailable in {current_lang.display_name()}, falling back to {lang.display_name()}"
                >
                <span class="fallback-lang-sq">[{lang.language}]</span>
                {self}
                </span>
            """


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
        fallback=TitleTranslatedStr,
        help_text=_("The name for a book. (Multilingal field)"),
    )
    author = models.TextField(
        help_text=_("The name of the person who wrote the book (Single language field)")
    )
    description = fields.Translated(
        models.TextField(help_text=_("Short details about a book. (Multilingal field)"))
    )
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
