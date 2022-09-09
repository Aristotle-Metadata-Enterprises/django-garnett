from django.utils.translation import get_language

from garnett.utils import lang_param


def query(request):
    return request.GET.get(lang_param(), None)


def cookie(request):
    return request.COOKIES.get("GARNETT_LANGUAGE_CODE", None)


def session(request):
    return request.session.get("GARNETT_LANGUAGE_CODE", None)


def header(request):
    return request.META.get("HTTP_X_GARNETT_LANGUAGE_CODE", None)


def browser(request):
    return get_language()
