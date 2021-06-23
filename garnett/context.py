from contextlib import ContextDecorator
import contextvars
from langcodes import Language

# Internal context var should be set via set_field_language and get via get_current_language
_ctx_language = contextvars.ContextVar("garnett_language")


class set_field_language(ContextDecorator):
    def __init__(self, language):
        if isinstance(language, Language):
            self.language = language
        else:
            self.language = Language.get(language)
        self.token = None

    def __enter__(self):
        self.token = _ctx_language.set(self.language)

    def __exit__(self, exc_type, exc_value, traceback):
        _ctx_language.reset(self.token)
