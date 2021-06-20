from django.http import Http404
from django.utils.translation import gettext as _

import logging

from .utils import get_language_from_request, is_valid_language
from .context import set_field_language

logger = logging.getLogger(__name__)


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
            return response


class TranslationContextNotFoundMiddleware(TranslationContextMiddleware):
    """
    This middleware catches the requested "garnett language" and:
     * sets a garnett language attribute on the request
     * defines a context variable that is used when reading or altering fields
     * will raise a 404 if the request language is not in languages list
    """

    def validate(self, language):
        if not is_valid_language(language):
            lang_obj = language
            lang_name = lang_obj.display_name(language)
            lang_en_name = lang_obj.display_name()
            raise Http404(
                _("This server does not support %(lang_name)s" " [%(lang_en_name)s].")
                % {
                    "lang_name": lang_name,
                    "lang_en_name": lang_en_name,
                }
            )


class TranslationCacheMiddleware:
    """Middleware to cache the garnett language in the users session storage

    This must be after one of the above middlewares and after the session middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, "garnett_language") and hasattr(request, "session"):
            request.session["GARNETT_LANGUAGE_CODE"] = request.garnett_language
        else:
            logger.error(
                "TranslationCacheMiddleware must come after main garnett middleware "
                "and the session middleware."
            )

        return self.get_response(request)
