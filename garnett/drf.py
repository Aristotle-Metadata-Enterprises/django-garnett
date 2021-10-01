"""
Helper methods for working with django-rest-framework
"""

from enum import Enum
from rest_framework.fields import JSONField, empty
from rest_framework import serializers

from garnett.fields import TranslatedField


class LanguageTypes(Enum):
    monolingual = 1
    multilingual = 2


class TranslatableAPIField(JSONField):
    def __init__(self, *args, **kwargs):
        self.innerfield = kwargs.pop("innerfield", None)
        super().__init__(*args, **kwargs)

    @property
    def validators(self):
        if not hasattr(self, "_validators"):
            self._validators = self.get_validators()

        if self.translation_type == LanguageTypes.monolingual:
            return self.innerfield.validators
        else:
            return self._validators

    @validators.setter
    def validators(self, validators):
        self._validators = validators

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data
        value = self.to_internal_value(data)

        if isinstance(data, str):
            self.translation_type = LanguageTypes.monolingual
        elif isinstance(data, dict):
            self.translation_type = LanguageTypes.multilingual
        else:
            # This branch shouldn't occur, but we'll let it pass.
            # This will get caught in the main validators.
            self.translation_type = LanguageTypes.multilingual
        self.run_validators(value)
        return value


translatable_serializer_field_mapping = {TranslatedField: TranslatableAPIField}
translatable_serializer_field_mapping.update(
    serializers.ModelSerializer.serializer_field_mapping.copy()
)


class TranslatableSerializerMixin:
    serializer_field_mapping = translatable_serializer_field_mapping

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )
        if field_class is TranslatableAPIField:
            field_kwargs["innerfield"] = model_field.field
        return field_class, field_kwargs
