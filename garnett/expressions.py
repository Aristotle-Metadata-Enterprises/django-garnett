from django.db.models import F
from django.db.models.fields.json import KeyTextTransform

from garnett.utils import get_current_language_code
from garnett.fields import TranslatedField


# Based on: https://code.djangoproject.com/ticket/29769#comment:5
# Updated comment here
# https://code.djangoproject.com/ticket/31639
class LangF(F):
    def resolve_expression(self, *args, **kwargs):
        print(args[0], kwargs)

        rhs = super().resolve_expression(*args, **kwargs)

        field_list = self.name.split("__")
        transforms = [
            field
            for field in field_list
            if field in rhs.field.__class__.class_lookups.keys()
        ]
        field_list = [
            field
            for field in field_list
            if field not in rhs.field.__class__.class_lookups.keys()
        ]
        self.name = "__".join(field_list)

        rhs = super().resolve_expression(*args, **kwargs)
        if isinstance(rhs.field, TranslatedField):
            field_list = self.name.split("__")

            if len(field_list) == 1:
                # Lookup current lang for one field
                field_list.extend([get_current_language_code()])

            for name in field_list[1:]:
                # Perform key lookups along path
                rhs = KeyTextTransform(name, rhs)

        lookups = rhs.field.__class__.class_lookups
        for transform in transforms:
            rhs = lookups[transform](rhs)

        return rhs


# TODO: should this just inherit from LangF or do we want one without reference lookups
class L(KeyTextTransform):
    """Expression to return the current language"""

    def __init__(self, *args, **kwargs):
        super().__init__(get_current_language_code(), *args, **kwargs)
