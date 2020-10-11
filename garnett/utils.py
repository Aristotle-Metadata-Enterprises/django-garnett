from django.conf import settings


def get_default_language():
    return settings.GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE


def get_current_language():
    from .context import ctx_language
    default_lang = get_default_language()
    lang = ctx_language.get(default_lang)
    return lang


def get_languages():
    langs = settings.GARNETT_TRANSLATABLE_LANGUAGES
    if callable(langs):
        return langs()
    if type(langs) == list:
        return langs
    return []

