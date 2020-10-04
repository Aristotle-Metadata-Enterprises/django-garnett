from .fields import get_default_language
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
