from typing import Tuple, Optional, Callable
from django.utils.translation import gettext as _

from langcodes import Language
from garnett.utils import (
    codes_to_langs,
    get_current_language,
    get_current_language_code,
    get_languages,
)


class HTMLTranslationMixin:
    def __html__(self) -> str:
        # Add leading [lang] wrapped in a span
        text = self
        if not self.is_fallback:
            return text
        elif not self.fallback_language:
            return "??"
        else:
            return (
                '<span class="fallback"'
                'data-lang-code="{lang}"'
                ">"
                "[{lang}]</span> "
                "{s}"
            ).format(s=self, lang=self.fallback_language.to_tag())


class TranslatedStr(str):
    """
    A translated string subclasses string and allows us to attach more information about
    how a string was generated and the language of the string.
    """

    def __new__(cls, content, fallback: Callable = None):
        current_language_code = get_current_language_code()
        has_current_language = current_language_code in content.keys()

        if has_current_language:
            fallback_language = None
            text = content.get(current_language_code)
        else:
            if fallback:
                fallback_language, text = fallback(content)
            else:
                fallback_language, text = cls.get_fallback_text(content)

        instance = super().__new__(cls, text)
        instance.translations = codes_to_langs(content)
        instance.is_fallback = not has_current_language
        instance.fallback_language = fallback_language
        return instance

    @classmethod
    def get_fallback_text(cls, content) -> Tuple[Optional[Language], str]:
        return None, ""


class VerboseTranslatedStr(TranslatedStr):
    """
    A translated string that gives information if a string isn't present.
    """

    @classmethod
    def get_fallback_text(cls, content):
        """Default fallback function that returns an error message"""
        language = get_current_language()
        lang_name = language.display_name(language)
        lang_en_name = language.display_name()

        return language, content.get(
            language.to_tag(),
            _(
                "No translation of this field available in %(lang_name)s"
                " [%(lang_en_name)s]."
            )
            % {
                "lang_name": lang_name,
                "lang_en_name": lang_en_name,
            },
        )


class NextTranslatedStr(TranslatedStr, HTMLTranslationMixin):
    """
    A translated string that fallsback based on the order of preferred langages in the app.
    """

    @classmethod
    def get_fallback_text(cls, content):
        """Fallback that checks each language consecutively"""
        for lang in get_languages():
            if lang.to_tag() in content:
                return lang, content[lang.to_tag()]

        return None, ""
