from django.conf import settings

def lang_param():
    return getattr(settings, 'GARNETT_QUERY_PARAMATER_NAME', 'glang')

def get_default_language():
    return getattr(settings, 'GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE', "en-AU")


def get_current_language():
    from .context import ctx_language
    default_lang = get_default_language()
    lang = ctx_language.get(default_lang)
    return lang


def get_languages():
    langs = getattr(settings, 
        'GARNETT_TRANSLATABLE_LANGUAGES',
        [get_default_language()]
    )
    if callable(langs):
        return langs()
    if type(langs) == list:
        return langs
    return []


def get_language_from_request(request):
    opt_order = getattr(settings, 
        'GARNETT_REQUEST_LANGUAGE_SELECTORS', ['query', 'cookie', 'header']
    )
    language_opts = {
        'query': request.GET.get(lang_param(), None),
        'cookie': request.COOKIES.get("GARNETT_LANGUAGE_CODE", None),
        'header': request.META.get("HTTP_X_GARNETT_LANGUAGE_CODE", None),
    }
    for opt in opt_order:
        if lang := language_opts.get(opt, None):
            return lang
    return get_default_language()
