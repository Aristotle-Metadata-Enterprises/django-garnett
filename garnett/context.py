from contextlib import ContextDecorator

import contextvars

ctx_language = contextvars.ContextVar("garnett_language")


class set_field_language(ContextDecorator):
    def __init__(self, language, deactivate=False):
        self.language = language
        ctx_language.set(language)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass
