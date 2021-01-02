from django.conf import settings
from django.utils.translation import get_language


def lang_param():
    return getattr(settings, "GARNETT_QUERY_PARAMATER_NAME", "glang")


def query(request):
    return request.GET.get(lang_param(), None)


def cookie(request):
    return request.COOKIES.get("GARNETT_LANGUAGE_CODE", None)


def header(request):
    return request.META.get("HTTP_X_GARNETT_LANGUAGE_CODE", None)


def browser(request):
    return get_language()
