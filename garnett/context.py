from contextlib import ContextDecorator
import contextvars

from garnett.utils import get_default_language

ctx_language = contextvars.ContextVar("garnett_language")


class set_field_language(ContextDecorator):
    def __init__(self, language, deactivate=False):
        self.old_language = ctx_language.set(language).old_value
        if self.old_language == contextvars.Token.MISSING:
            self.old_language = get_default_language()
        self.deactivate = deactivate

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        # Using Context.reset like shown below causes wierd errors
        # TODO: Myabe fix this?
        # ctx_language.reset(self.language)
        ctx_language.set(self.old_language)
