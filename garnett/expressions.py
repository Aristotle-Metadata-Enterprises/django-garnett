from django.db.models import F
from django.db.models.fields.json import KeyTextTransform

from garnett.utils import get_current_language
from garnett.fields import TranslatedField


# Based on: https://code.djangoproject.com/ticket/29769#comment:5
class LangF(F):
    def resolve_expression(
        self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False
    ):
        rhs = super().resolve_expression(query, allow_joins, reuse, summarize, for_save)
        if isinstance(rhs.field, TranslatedField):
            field_list = self.name.split("__")
            # TODO: should this always lookup lang
            if len(field_list) == 1:
                # Lookup current lang for one field
                field_list.extend([get_current_language()])
            for name in field_list[1:]:
                # Perform key lookups along path
                rhs = KeyTextTransform(name, rhs)
        return rhs


# TODO: should this just inherit from LangF or do we want one without reference lookups
class L(KeyTextTransform):
    """Expression to return the current language"""

    def __init__(self, *args, **kwargs):
        super().__init__(get_current_language(), *args, **kwargs)
