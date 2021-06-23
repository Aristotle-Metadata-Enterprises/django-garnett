from contextlib import ContextDecorator
from django.core.exceptions import FieldError
from django.db.models.sql import query
from dataclasses import dataclass
from typing import Any
import functools

from garnett.fields import TranslatedField
from garnett.utils import get_current_language


# Save current join info
_JoinInfo = query.JoinInfo


@dataclass
class JoinInfo:
    final_field: Any
    targets: Any
    opts: Any
    joins: Any
    path: Any
    transform_function_func: Any

    @property
    def transform_function(self):
        if isinstance(self.final_field, TranslatedField):
            # If its a partial, it must have had a transformer applied - leave it alone!
            if isinstance(self.transform_function_func, functools.partial):

                return self.transform_function_func

            name = get_current_language()

            # Cloned in from django
            def transform(field, alias, *, name, previous):
                try:
                    wrapped = previous(field, alias)
                    return self.try_transform(wrapped, name)
                except FieldError:
                    # TODO: figure out how to handle this case as we don't have
                    # final_field or last_field_exception

                    # FieldError is raised if the transform doesn't exist.
                    # if isinstance(final_field, Field) and last_field_exception:
                    #     raise last_field_exception
                    # else:
                    #     raise
                    raise

            # -------------------

            return functools.partial(
                transform, name=name, previous=self.transform_function_func
            )

        return self.transform_function_func

    def try_transform(self, lhs, name):
        # Cloned in from django
        import difflib

        """
        Helper method for build_lookup(). Try to fetch and initialize
        a transform for name parameter from lhs.
        """
        transform_class = lhs.get_transform(name)
        if transform_class:
            return transform_class(lhs)
        else:
            output_field = lhs.output_field.__class__
            suggested_lookups = difflib.get_close_matches(
                name, output_field.get_lookups()
            )
            if suggested_lookups:
                suggestion = ", perhaps you meant %s?" % " or ".join(suggested_lookups)
            else:
                suggestion = "."
            raise FieldError(
                "Unsupported lookup '%s' for %s or join on the field not "
                "permitted%s" % (name, output_field.__name__, suggestion)
            )

    def __iter__(self):
        # Necessary to mimic a tuple
        for x in [
            self.final_field,
            self.targets,
            self.opts,
            self.joins,
            self.path,
            self.transform_function,
        ]:
            yield x


def apply_patches():
    """Apply monkey patches to django"""
    # This is needed to allow values/values_list and F lookups to work
    # The most dangerous monkey patch of all time
    query.JoinInfo = JoinInfo


def revert_patches():
    """Revert monkey patches to django"""
    query.JoinInfo = _JoinInfo


class patch_lookups(ContextDecorator):
    def __enter__(self):
        apply_patches()

    def __exit__(self, exc_type, exc_value, traceback):
        revert_patches()
