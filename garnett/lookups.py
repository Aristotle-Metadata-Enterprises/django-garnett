from django.db.models.fields import json
from django.db.models import lookups
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.contrib.postgres.lookups import SearchLookup, TrigramSimilar
from django.contrib.postgres.search import TrigramSimilarity

from garnett.fields import TranslatedFieldBase
from garnett.utils import get_current_language


# We duplicate and process_lhs and process_rhs to be certain these are
# Actually called during tests.
# Otherwise, the blank classes appear to give 100% coverage


class CurrentLanguageMixin:
    def __init__(self, kt, *args, **kwargs):
        x = json.KeyTransform(
            str(get_current_language()),
            kt,
        )
        args = list(args)
        args.insert(0, x)
        super().__init__(*args, **kwargs)


@TranslatedFieldBase.register_lookup
class HasLang(json.HasKey):
    lookup_name = "has_lang"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class HasLangs(json.HasKeys):
    lookup_name = "has_langs"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class HasAnyLangs(json.HasAnyKeys):
    lookup_name = "has_any_langs"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


# @TranslatedFieldBase.register_lookup
# class Exact(CurrentLanguageMixin, json.KeyTransformExact):
#     pass


@TranslatedFieldBase.register_lookup
class Exact(CurrentLanguageMixin, json.KeyTransformIExact):
    # It says iexact - but it actuall works?!?
    # TODO: Find out why
    lookup_name = "exact"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class IExact(CurrentLanguageMixin, json.KeyTransformIExact):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageIContains(CurrentLanguageMixin, json.KeyTransformIContains):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageContains(
    CurrentLanguageMixin, json.KeyTransformTextLookupMixin, lookups.Contains
):
    lookup_name = "contains"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


# We add a "contains" to allow this lookup on non-Postgres databases
class KeyTransformContains(json.KeyTransformTextLookupMixin, lookups.Contains):
    lookup_name = "contains"

    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


json.KeyTransform.register_lookup(KeyTransformContains)


@TranslatedFieldBase.register_lookup
class BaseLanguageWith(CurrentLanguageMixin, json.KeyTransformStartsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageIStartsWith(CurrentLanguageMixin, json.KeyTransformIStartsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageEndsWith(CurrentLanguageMixin, json.KeyTransformEndsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageIEndsWith(CurrentLanguageMixin, json.KeyTransformIEndsWith):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageRegex(CurrentLanguageMixin, json.KeyTransformRegex):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageIRegex(CurrentLanguageMixin, json.KeyTransformIRegex):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


@TranslatedFieldBase.register_lookup
class BaseLanguageSearch(
    CurrentLanguageMixin, json.KeyTransformTextLookupMixin, SearchLookup
):
    def process_lhs(self, compiler, connection):
        return super().process_lhs(compiler, connection)

    def process_rhs(self, compiler, connection):
        return super().process_rhs(compiler, connection)


# --- Postgres only functions ---


@TranslatedFieldBase.register_lookup
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
