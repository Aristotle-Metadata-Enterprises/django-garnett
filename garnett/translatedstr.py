from typing import Tuple, Optional, Callable
from django.utils.translation import gettext as _

from langcodes import Language
from garnett.utils import get_current_language, get_current_language_code, get_languages


class HTMLTranslationMixin:
    def __html__(self) -> str:
        # Add leading [lang] wrapped in a span
        text = self
        print(f"{self.is_fallback=}")
        if not self.is_fallback:
            return text
        elif not self.fallback_language:
            return "??"
        else:
            return (
                '<span class="fallback"'
                'data-lang-code="{lang.language}"'
                ">"
                "[{lang.language}]</span> "
                "{s}"
            ).format(s=self, lang=self.fallback_language)


class TranslatedStr(str):
    def __new__(cls, content, fallback: Callable = None):
        current_language_code = get_current_language_code()
        has_current_language = current_language_code in content.keys()
        if has_current_language:
            is_fallback = False
            fallback_language = None
            text = content.get(current_language_code)
        else:
            is_fallback = True
            if fallback:
                fallback_language, text = fallback(content)
            else:
                fallback_language, text = cls.get_fallback_text(content)

        instance = super().__new__(cls, text)
        instance.translations = content
        instance.is_fallback = is_fallback
        instance.fallback_language = fallback_language
        return instance

    @classmethod
    def get_fallback_text(cls, content) -> Tuple[Optional[Language], str]:
        return None, ""


class VerboseTranslatedStr(TranslatedStr):
    @classmethod
    def get_fallback_text(cls, content):
        """Default fallback function that returns an error message"""
        language = get_current_language()
        lang_name = language.display_name(language)
        lang_en_name = language.display_name()

        return language, content.get(
            language.language,
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
    @classmethod
    def get_fallback_text(cls, content):
        """Fallback that checks each language consecutively"""
        for lang in get_languages():
            if lang.language in content:
                # self.fallback_language = lang
                return lang, content[lang.language]

        return None, ""
