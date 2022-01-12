from contextlib import ContextDecorator
import contextvars
from langcodes import Language

# Internal context var should be set via set_field_language and get via get_current_language
_ctx_language = contextvars.ContextVar("garnett_language")
_ctx_force_blank = contextvars.ContextVar("garnett_language_blank")


class set_field_language(ContextDecorator):
    def __init__(self, language, force_blank=False):
        if isinstance(language, Language):
            self.language = language
        else:
            self.language = Language.get(language)
        self.token = None
        self.token_blank = None
        self.force_blank = force_blank

    def __enter__(self):
        self.token = _ctx_language.set(self.language)
        self.token_blank = _ctx_force_blank.set(self.force_blank)

    def __exit__(self, exc_type, exc_value, traceback):
        _ctx_language.reset(self.token)
        _ctx_force_blank.reset(self.token_blank)
