from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from garnett import fields
from garnett.translatedstr import TranslatedStr
from garnett.utils import get_languages, get_current_language
from library_app.managers import BookQuerySet


RANDOM_STR = "f6e56ce9-cc87-45ac-8a19-8c34136e6f52"
BLEACH_STR = "string to be replace"


class CustomTestingField(models.TextField):
    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Note: If there is data migration when migrating to TranslatedField, the manually added
         step_1_safe_encode_content() function in the migration file will base64 encode the value in the field
         before get_db_prep_value is called.

         For example:
            old value = "this is a book"
            new value = '{"en": "dGhpcyBpcyBhIGJvb2s="}'

        The new value is then parse to the get_db_prep_value() function.
        If custom get_db_prep_value() function is used you will need to make sure that the custom get_db_prep_value() function is
        not modifying the input value.

        Some examples,
            1. if the custom get_db_prep_value() function append a fix str to all input value:
                    input value = '{"en": "dGhpcyBpcyBhIGJvb2s="}'
                    return value = '{"en": "dGhpcyBpcyBhIGJvb2s="}1234567'
               this would raise "django.db.utils.DataError: invalid input syntax for type json" because the return value
               from the custom get_db_prep_value() function is not valid json

            2. if the custom get_db_prep_value() function bleach certain substring (e.g dGhpcy) on the input value:
                    input value = '{"en": "dGhpcyBpcyBhIGJvb2s="}'
                    return value = '{"en": "BpcyBhIGJvb2s="}'
               this would modify the base64 value and decoding the modfied base64 value would return unexpected result
        """
        if value is None:
            return super().get_db_prep_value(value, connection, prepared)
        bleached_value = value.replace(BLEACH_STR, RANDOM_STR)
        return super().get_db_prep_value(bleached_value, connection, prepared)


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
    objects = BookQuerySet.as_manager()

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

    other_info = fields.Translated(CustomTestingField(blank=True, default=""))

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
