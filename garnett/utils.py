from django.conf import settings
from django.utils.module_loading import import_string


def lang_param():
    return getattr(settings, "GARNETT_QUERY_PARAMATER_NAME", "glang")


def get_default_language():
    return getattr(settings, "GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE", "en-AU")


def get_property_name():
    return getattr(settings, "GARNETT_TRANSLATIONS_PROPERTY_NAME", "translations")


def get_current_language():
    from .context import ctx_language

    default_lang = get_default_language()
    lang = ctx_language.get(default_lang)
    return lang


def get_languages():
    langs = getattr(
        settings, "GARNETT_TRANSLATABLE_LANGUAGES", [get_default_language()]
    )
    if callable(langs):
        return langs()
    if type(langs) == list:
        return langs
    return []


def get_language_from_request(request):
    opt_order = getattr(
        settings,
        "GARNETT_REQUEST_LANGUAGE_SELECTORS",
        [
            "garnett.selectors.query",
            "garnett.selectors.cookie",
            "garnett.selectors.header",
        ],
    )
    for opt in opt_order:
        func = import_string(opt)
        if lang := func(request):
            return lang
    return get_default_language()
