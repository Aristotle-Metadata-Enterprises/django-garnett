from contextlib import ContextDecorator
import contextvars

ctx_language = contextvars.ContextVar("garnett_language")


class set_field_language(ContextDecorator):
    def __init__(self, language):
        self.language = language
        self.token = None

    def __enter__(self):
        self.token = ctx_language.set(self.language)

    def __exit__(self, exc_type, exc_value, traceback):
        ctx_language.reset(self.token)
