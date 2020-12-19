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


class TranslatedFieldBase(JSONField):
    def formfield(self, **kwargs):
        # We need to bypass the JSONField implementation
        return Field.formfield(self, **{
            'form_class': forms.CharField,
            **kwargs,
        })

    def get_attname(self):
        return self.name + "_tsall"

    def get_attname_column(self):
        attname = self.get_attname()
        column = self.db_column or self.name
        return attname, column

    def contribute_to_class(self, cls, name, private_only=False):
        # maybe us this instead of hacky get attr messing around
        super().contribute_to_class(cls, name, private_only)

        @property
        def translator(ego):
            "We use ego to diferentiate scope here as this is the inner self"
            "Maybe its not necessary, but it is funny"
            """I'm the 'x' property."""

            all_ts = getattr(ego, f'{name}_tsall')
            if type(all_ts) is not dict:
                logger.warning(
                    "DJANGO-GARNETT: Displaying an untranslatable field - model:{} (pk:{}), field:{}".format(
                        type(ego), ego.pk, name
                    )
                )
                return all_ts

            language = get_current_language()
            lang_name = Language.make(language=language).display_name(language)
            lang_en_name = Language.make(language=language).display_name()
            # TODO: Make this return None if no translation
            return all_ts.get(
                language,
                _(
                    "No translation of %(field)s available in %(lang_name)s"
                    " [%(lang_en_name)s]."
                ) % {
                    'field': name,
                    'lang_name': lang_name,
                    'lang_en_name': lang_en_name,
                }
            )

        @translator.setter
        def translator(ego, value):
            all_ts = getattr(ego, f'{name}_tsall')
            if type(all_ts) is not dict:
                logger.warning(
                    "DJANGO-GARNETT: Saving a broken field - model:{} (pk:{}), field:{}".format(
                        type(ego), ego.pk, name
                    )
                )
                logger.debug("DJANGO-GARNETT: Field data was - {}".format(all_ts))

                all_ts = {}
            all_ts[get_current_language()] = value

        setattr(cls, f'{name}', translator)
        
        @property
        def translations(ego):
            translations = {}  # don't want an immutable
            for field in ego._meta.get_fields():
                if isinstance(field, TranslatedFieldBase):
                    all_t = getattr(ego, f"{field.name}_tsall")
                    translations[field.name] = all_t
            return translations

        try:
            propname = settings.GARNETT_TRANSLATIONS_PROPERTY_NAME
        except:
            propname = 'translations'
        setattr(cls, propname, translations)


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