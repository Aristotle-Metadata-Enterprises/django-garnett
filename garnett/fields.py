import json

from django import forms
from django.db.models import Field, JSONField
from django.core import exceptions
from django.conf import settings



def get_default_language():
    return "en" # settings.DEFAULT_TRANSLATABLE_LANGUAGE


def get_current_language():
    return get_default_language()


def get_languages():
    langs = settings.TRANSLATABLE_LANGUAGES
    if callable(langs):
        return langs()
    if type(langs) == list:
        return langs
    return []


class TranslatedFieldBase(JSONField):
    def formfield(self, **kwargs):
        # We need to bypass the JSONField implementation
        return Field.formfield(self, **{
            'form_class': forms.CharField,
            **kwargs,
        })

    def pre_save(self, model_instance, add):
        """Return field's value just before saving."""
        return getattr(model_instance, f"{self.attname}_tsall")

    # def contribute_to_class(self, cls, name, private_only=False):
    #     maybe us this instead of hacky get attr messing around

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