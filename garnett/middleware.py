from django.http import Http404
from django.utils.translation import gettext as _

from langcodes import Language

from .utils import get_default_language, get_languages
from .context import set_field_language


class TranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request.language = request.GET.get("glang", get_default_language())
        with set_field_language(request.language):
            response = self.get_response(request)

            # Code to be executed for each request/response after
            # the view is called.

            return response


class TranslationNotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request.language = request.GET.get("glang", get_default_language())
        if request.language not in get_languages():
            language = request.language
            lang_name = Language.make(language=language).display_name(language)
            lang_en_name = Language.make(language=language).display_name()
            raise Http404(
                    _(
                        "This server does not support %(lang_name)s"
                        " [%(lang_en_name)s]."
                    ) % {
                        'lang_name': lang_name,
                        'lang_en_name': lang_en_name,
                    }
                )

        with set_field_language(request.language):
            response = self.get_response(request)

            # Code to be executed for each request/response after
            # the view is called.

            return response
