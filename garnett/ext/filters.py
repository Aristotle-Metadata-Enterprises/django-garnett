# Patches for django-filters
"""
This has been added as django-filters is used by multiple libraries,
including DRF and Djgnao-Graphene.
"""

from django_filters.filterset import CharFilter
from garnett.fields import TranslatedField


class TranslatedCharFilter(CharFilter):
    pass


def patch_filters():
    from django_filters.filterset import FILTER_FOR_DBFIELD_DEFAULTS

    FILTER_FOR_DBFIELD_DEFAULTS.update(
        {TranslatedField: {"filter_class": TranslatedCharFilter}}
    )

    from django_filters.rest_framework.filterset import FILTER_FOR_DBFIELD_DEFAULTS

    FILTER_FOR_DBFIELD_DEFAULTS.update(
        {TranslatedField: {"filter_class": TranslatedCharFilter}}
    )
