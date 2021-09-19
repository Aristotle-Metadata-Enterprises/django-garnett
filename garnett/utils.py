from typing import List, Union

from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from langcodes import Language

from garnett.context import _ctx_language


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
        language = Language.get(language)
    return language in get_languages()


def get_current_language() -> Language:
    lang = _ctx_language.get(None)
    if not lang:
        return get_default_language()
    return lang


def get_current_language_code() -> str:
    return get_current_language().to_tag()


def get_languages() -> List[Language]:
    langs = getattr(
        settings, "GARNETT_TRANSLATABLE_LANGUAGES", [get_default_language()]
    )
    if callable(langs):
        langs = langs()
    if type(langs) == list:
        return [Language.get(lang) for lang in langs]
    raise ImproperlyConfigured(
        "GARNETT_TRANSLATABLE_LANGUAGES must be a list or a callable that returns a list"
    )


def get_language_from_request(request) -> Language:
    opt_order = getattr(
        settings,
        "GARNETT_REQUEST_LANGUAGE_SELECTORS",
        [
            "garnett.selectors.header",
            "garnett.selectors.query",
            "garnett.selectors.cookie",
        ],
    )
    for opt in opt_order:
        func = import_string(opt)
        if lang := func(request):
            return Language.get(lang)
    return get_default_language()
