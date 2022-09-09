from django.db.models.query import BaseIterable
from garnett.expressions import L

PREFIX = "L_garnett__"


class TranslatableValuesIterable(BaseIterable):
    """
    Unwind the modifications that are made before calling .values()
    Iterable returned by QuerySet.values() that yields a dict for each row.
    """

    def clean_garnett_field(self, field_name) -> str:
        """Return the field name minus the prefix"""
        return field_name.replace(PREFIX, "")

    def __iter__(self):
        queryset = self.queryset
        query = queryset.query
        compiler = query.get_compiler(queryset.db)

        # extra(select=...) cols are always at the start of the row.
        names = [
            *query.extra_select,
            *query.values_select,
            *query.annotation_select,
        ]
        indexes = range(len(names))
        for row in compiler.results_iter(
            chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size
        ):
            yield {self.clean_garnett_field(names[i]): row[i] for i in indexes}


class TranslatedQuerySetMixin:
    """
    A translated QuerySet mixin to add extra functionality to translated fields
    Must be mixedin to a QuerySet
    """

    def values(self, *fields, **expressions):
        """
        .values() for translatable fields
        Still expects values to be passed with L()
        """

        # Convert anything that is an L from a field to an expression - so it treats it as an expression
        # rather than a field.
        # We will clean the field prefix in our custom iterable class "TranslatableQuerySetMixin"
        cleaned_fields = []
        for field in fields:
            if isinstance(field, L):
                expressions.update(
                    {f"{PREFIX}{field.source_expressions[0].name}": field}
                )
            else:
                cleaned_fields.append(field)

        clone = super().values(*cleaned_fields, **expressions)
        clone._iterable_class = TranslatableValuesIterable

        return clone
