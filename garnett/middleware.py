from django.http import Http404
from django.utils.translation import gettext as _

from langcodes import Language

from .utils import get_languages, get_language_from_request
from .context import set_field_language


class TranslationContextMiddleware:
    """
    This middleware catches the requested "garnett language" and:
     * sets a garnett language attribute on the request
     * defines a context variable that is used when reading or altering fields
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def validate(self, language):
        """Validate the language raising http errors if invalid"""
        return None

    def __call__(self, request):
        request.garnett_language = get_language_from_request(request)
        self.validate(request.garnett_language)
        with set_field_language(request.garnett_language):
            response = self.get_response(request)
            response.set_cookie("GARNETT_LANGUAGE_CODE", request.garnett_language)
            return response


class TranslationContextNotFoundMiddleware(TranslationContextMiddleware):
    """
    This middleware catches the requested "garnett language" and:
     * sets a garnett language attribute on the request
     * defines a context variable that is used when reading or altering fields
     * will raise a 404 if the request language is not in languages list
    """

    def validate(self, language):
        if language not in get_languages():
            lang_obj = Language.make(language=language)
            lang_name = lang_obj.display_name(language)
            lang_en_name = lang_obj.display_name()
            raise Http404(
                _("This server does not support %(lang_name)s" " [%(lang_en_name)s].")
                % {
                    "lang_name": lang_name,
                    "lang_en_name": lang_en_name,
                }
            )
