from django.db.models import QuerySet
from garnett.mixins import TranslatedQuerySetMixin


class BookQuerySet(TranslatedQuerySetMixin, QuerySet):
    pass
