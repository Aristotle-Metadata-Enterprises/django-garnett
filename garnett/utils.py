from typing import List, Union, Optional

import langcodes.tag_parser
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from langcodes import Language

from garnett.context import _ctx_language, _ctx_force_blank


def lang_param():
    return getattr(settings, "GARNETT_QUERY_PARAMETER_NAME", "glang")


def get_default_language():
    setting = getattr(settings, "GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE", "en-AU")
    if callable(setting):
        default = setting()
    else:
        default = setting

    if isinstance(default, Language):
        return default
    elif isinstance(default, str):
        return Language.get(default)
    else:
        raise ImproperlyConfigured(
            "GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE must be a string or callable that returns a string or `Language` object"
        )


def codes_to_langs(content: dict) -> dict:
    return {Language.get(lang): text for lang, text in content.items()}


def get_property_name() -> str:
    return getattr(settings, "GARNETT_TRANSLATIONS_PROPERTY_NAME", "translations")


def normalise_language_code(langcode):
    return Language.get(langcode).to_tag()


def normalise_language_codes(value):
    return {normalise_language_code(lang): val for lang, val in value.items()}


def is_valid_language(language: Union[str, Language]) -> bool:
    if isinstance(language, Language):
        language = language
    if isinstance(language, str):
        try:
            language = Language.get(language)
        except langcodes.tag_parser.LanguageTagError:
            return False
    return language in get_languages()


def get_current_language() -> Language:
    lang = _ctx_language.get(None)
    if not lang:
        return get_default_language()
    return lang


def get_current_language_code() -> str:
    return get_current_language().to_tag()


def get_current_blank_override() -> bool:
    return _ctx_force_blank.get(False)


def get_safe_language(lang_code: str) -> Optional[Language]:
    """Return language if language for lang code exists, otherwise none"""
    try:
        return Language.get(lang_code)
    except langcodes.tag_parser.LanguageTagError:
        return None


def validate_language_list(langs) -> List[Language]:
    """
    Validate and clean a potential list of languages.
    This may return an empty list if the provided languages are invalid
    """
    if type(langs) is not list:
        return []

    languages = []
    for lang_code in langs:
        if language := get_safe_language(lang_code):
            languages.append(language)

    if languages:
        return languages


def get_languages() -> List[Language]:
    langs = getattr(
        settings, "GARNETT_TRANSLATABLE_LANGUAGES", [get_default_language()]
    )
    if callable(langs):
        langs = langs()

    languages = validate_language_list(langs)

    if not languages:
        raise ImproperlyConfigured(
            "GARNETT_TRANSLATABLE_LANGUAGES must be a list of languages or a callable that returns a list of languages"
        )
    return languages
