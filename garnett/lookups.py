from django.db.models import lookups
from django.db.models.fields import json, CharField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.contrib.postgres.lookups import SearchLookup, TrigramSimilar
from django.contrib.postgres.search import TrigramSimilarity

from garnett.fields import TranslatedField, TranslatedKeyTransform
from garnett.utils import get_current_language


# We duplicate and process_lhs and process_rhs to be certain these are
# Actually called during tests.
# Otherwise, the blank classes appear to give 100% coverage


@TranslatedField.register_lookup
class HasLang(json.HasKey):
    lookup_name = "has_lang"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class HasLangs(json.HasKeys):
    lookup_name = "has_langs"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class HasAnyLangs(json.HasAnyKeys):
    lookup_name = "has_any_langs"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


# Override default lookups on our field to handle language lookups


class CurrentLanguageMixin:
    """Mixin to perform language lookup on lhs"""

    def __init__(self, lhs, *args, **kwargs):
        tlhs = json.KeyTransform(
            str(get_current_language()),
            lhs,
        )
        super().__init__(tlhs, *args, **kwargs)


@TranslatedField.register_lookup
class BaseLanguageExact(
    CurrentLanguageMixin, json.KeyTransformTextLookupMixin, lookups.Exact
):
    # Note: On some database engines lookup_name actually has an effect on the result
    # (See lookup_cast in the django postgres backend)
    lookup_name = "exact"
    prepare_rhs = False

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageIExact(CurrentLanguageMixin, json.KeyTransformIExact):
    lookup_name = "iexact"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageIContains(CurrentLanguageMixin, json.KeyTransformIContains):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageContains(
    CurrentLanguageMixin, json.KeyTransformTextLookupMixin, lookups.Contains
):
    # Override the default json field contains which is not a text contains
    # https://docs.djangoproject.com/en/3.1/topics/db/queries/#contains
    lookup_name = "contains"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


# Override contains lookup for after a key lookup i.e. title__en__contains="thing"
@TranslatedKeyTransform.register_lookup
class KeyTransformContains(json.KeyTransformTextLookupMixin, lookups.Contains):
    lookup_name = "contains"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedKeyTransform.register_lookup
class KeyTransformExact(json.KeyTransformExact):
    def process_lhs(self, compiler, connection):
        self.lhs = Cast(self.lhs, CharField())
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        self.rhs = Cast(self.lhs, CharField())
        return super().process_lhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageStartsWith(CurrentLanguageMixin, json.KeyTransformStartsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageIStartsWith(CurrentLanguageMixin, json.KeyTransformIStartsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageEndsWith(CurrentLanguageMixin, json.KeyTransformEndsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageIEndsWith(CurrentLanguageMixin, json.KeyTransformIEndsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageRegex(CurrentLanguageMixin, json.KeyTransformRegex):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageIRegex(CurrentLanguageMixin, json.KeyTransformIRegex):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedField.register_lookup
class BaseLanguageSearch(
    CurrentLanguageMixin, json.KeyTransformTextLookupMixin, SearchLookup
):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


# --- Postgres only functions ---


@TranslatedField.register_lookup
class BaseLanguageTrigramSimilar(
    CurrentLanguageMixin, json.KeyTransformTextLookupMixin, TrigramSimilar
):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


class LangTrigramSimilarity(TrigramSimilarity):
    # There is no way we can calculate if a field is a language or not
    # So we have to write our own function here
    # We also need to cast the JSONB field to a string
    def __init__(self, expression, string, **extra):
        lang = str(get_current_language())
        expression = KeyTextTransform(lang, expression)
        super().__init__(expression, string, **extra)
