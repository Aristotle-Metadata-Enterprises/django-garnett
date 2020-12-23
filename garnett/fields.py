import json

from django import forms
from django.db.models import Field, JSONField
from django.core import exceptions
from django.conf import settings


from django.utils.translation import gettext as _
from garnett.utils import get_current_language
from langcodes import Language

import logging

# Get an instance of a logger
logger = logging.getLogger("DJANGO_GARNETT")


def translation_fallback(field, obj):
    all_ts = getattr(obj, f'{field.name}_tsall')
    language = get_current_language()
    lang_name = Language.make(language=language).display_name(language)
    lang_en_name = Language.make(language=language).display_name()
    return all_ts.get(
        language,
        _(
            "No translation of %(field)s available in %(lang_name)s"
            " [%(lang_en_name)s]."
        ) % {
            'field': field.name,
            'lang_name': lang_name,
            'lang_en_name': lang_en_name,
        }
    )                


def blank_fallback(field, obj):
    return ""


class TranslatedFieldBase(JSONField):

    def __init__(self, *args, fallback=None, **kwargs):
        if fallback:
            self.fallback = fallback
        else:
            self.fallback = translation_fallback
        super().__init__(self, *args, **kwargs)

    def formfield(self, **kwargs):
        # We need to bypass the JSONField implementation
        return Field.formfield(self, **{
            'form_class': forms.CharField,
            **kwargs,
        })

    def get_attname(self):
        return self.name + "_tsall"

    def value_from_object(self, obj):
        """Return the value of this field in the given model instance."""
        all_ts = getattr(obj, f'{self.name}_tsall')
        if type(all_ts) is not dict:
            logger.warning(
                "DJANGO-GARNETT: Displaying an untranslatable field - model:{} (pk:{}), field:{}".format(
                    type(obj), obj.pk, name
                )
            )
            return str(all_ts)

        language = get_current_language()
        return all_ts.get(
            language,
            None
        )

    def get_attname_column(self):
        attname = self.get_attname()
        column = self.db_column or self.name
        return attname, column

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        # We use ego to diferentiate scope here as this is the inner self
        # Maybe its not necessary, but it is funny

        @property
        def translator(ego):
            value = self.value_from_object(ego) 
            if value is not None:
                return value
            else:
                all_ts = getattr(ego, f'{name}_tsall')
                language = get_current_language()
                lang_name = Language.make(language=language).display_name(language)
                lang_en_name = Language.make(language=language).display_name()
                return self.fallback(self, ego)             

        @translator.setter
        def translator(ego, value):
            all_ts = getattr(ego, f'{name}_tsall')
            if not all_ts:
                # This is probably the first save through
                all_ts = {}
            elif type(all_ts) is not dict:
                logger.warning(
                    "DJANGO-GARNETT: Saving a broken field - model:{} (pk:{}), field:{}".format(
                        type(ego), ego.pk, name
                    )
                )
                logger.debug("DJANGO-GARNETT: Field data was - {}".format(all_ts))

                all_ts = {}
            if isinstance(value, str):
                all_ts[get_current_language()] = value
            elif isinstance(value, dict):
                # Can assign dict, but all ekys and values must be strings
                def is_string(value):
                    return isinstance(value, str)
                assert all(map(lambda a: is_string(a), value.keys()))
                assert all(map(lambda a: is_string(a), value.values()))
                #TODO: validate that all keys are valid language codes
                all_ts.update(value)
            else:
                raise TypeError("Invalid value assigned to translatable")
            setattr(ego, f'{name}_tsall', all_ts)

        setattr(cls, f'{name}', translator)
        
        # This can probably be cached on the class
        @property
        def translatable_fields(ego):
            return [
                field for field in ego._meta.get_fields()
                if isinstance(field, TranslatedFieldBase)
            ]
        try:
            propname = settings.GARNETT_TRANSLATABLE_FIELDS_PROPERTY_NAME
        except:
            propname = 'translatable_fields'
        setattr(cls, propname, translatable_fields)


        @property
        def translations(ego):
            from dataclasses import make_dataclass

            translatable_fields = ego.translatable_fields
            print(translatable_fields)
            Translations = make_dataclass(
                'Translations',
                [(f.name, dict) for f in translatable_fields]
            )
            kwargs = {}
            for field in translatable_fields:
                kwargs[field.name] = getattr(ego, f"{field.name}_tsall")
            return Translations(**kwargs)

        try:
            propname = settings.GARNETT_TRANSLATIONS_PROPERTY_NAME
        except:
            propname = 'translations'
        setattr(cls, propname, translations)

    def run_validators(self, values):
        if values in self.empty_values:
            return

        errors = []
        for value in values.values():
            for v in self.validators:
                try:
                    v(value)
                except exceptions.ValidationError as e:
                    if hasattr(e, 'code') and e.code in self.error_messages:
                        e.message = self.error_messages[e.code]
                    errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)


    # def get_prep_value(self, value):
    #     try:
    #         import ast
    #         value = ast.literal_eval(value)
    #         # value = json.loads(value)
    #     except: # json.JSONDecodeError:
    #         pass
    #     if type(value) == str:
    #         value = {get_default_language(): value}
    #     elif type(value) == dict:
    #         for val in value.values():
    #             if type(val) != str:
    #                 raise exceptions.ValidationError("text not string")
    #         for key in value.keys():
    #             if key not in get_languages():
    #                 raise exceptions.ValidationError("not allowed translate")
    #     else:
    #         raise exceptions.ValidationError(
    #             "not valid",
    #             code='invalid',
    #             params={'value': value},
    #         )

    #     return super().get_prep_value(value)

    # def from_db_value(self, value, expression, connection):
    #     if value is None:
    #         return value
    #     try:
    #         return json.loads(value, cls=self.decoder)
    #     except json.JSONDecodeError:
    #         return value


class TranslatedCharField(TranslatedFieldBase):
    pass


class TranslatedTextField(TranslatedFieldBase):
    def formfield(self, **kwargs):
        return super().formfield(**{
            'widget': forms.Textarea,
            **kwargs,
        })


from django.db.models.fields import json
from django.db.models import lookups


@TranslatedFieldBase.register_lookup
class HasLang(json.HasKey):
    lookup_name = 'has_lang'


@TranslatedFieldBase.register_lookup
class HasLangs(json.HasKeys):
    lookup_name = 'has_langs'


@TranslatedFieldBase.register_lookup
class HasAnyLangs(json.HasAnyKeys):
    lookup_name = 'has_any_langs'


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
class Exact(CurrentLanguageMixin, json.KeyTransformIExact):
    pass


@TranslatedFieldBase.register_lookup
class IExact(CurrentLanguageMixin, json.KeyTransformExact):
    pass


@TranslatedFieldBase.register_lookup
class BaseLanguageIContains(CurrentLanguageMixin, json.KeyTransformIContains):
    pass


@TranslatedFieldBase.register_lookup
class BaseLanguageContains(CurrentLanguageMixin, json.KeyTransformTextLookupMixin, lookups.Contains):
    lookup_name = 'contains'

json.KeyTransform.register_lookup(BaseLanguageContains)


@TranslatedFieldBase.register_lookup
class BaseLanguageWith(CurrentLanguageMixin, json.KeyTransformStartsWith):
    pass


@TranslatedFieldBase.register_lookup
class BaseLanguageIStartsWith(CurrentLanguageMixin, json.KeyTransformIStartsWith):
    pass


@TranslatedFieldBase.register_lookup
class BaseLanguageEndsWith(CurrentLanguageMixin, json.KeyTransformEndsWith):
    pass


@TranslatedFieldBase.register_lookup
class BaseLanguageIEndsWith(CurrentLanguageMixin, json.KeyTransformIEndsWith):
    pass


@TranslatedFieldBase.register_lookup
class BaseLanguageRegex(CurrentLanguageMixin, json.KeyTransformRegex):
    pass


@TranslatedFieldBase.register_lookup
class BaseLanguageIRegex(CurrentLanguageMixin, json.KeyTransformIRegex):
    pass
