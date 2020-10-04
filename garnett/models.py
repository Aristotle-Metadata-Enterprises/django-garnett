from django.db import models
from django.core.exceptions import FieldDoesNotExist
from garnett import fields
from garnett.fields import get_current_language


class Translatable(models.Model):

    translations = {}

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translations = {}  # don't want an immutable
        for field in self._meta.get_fields():
            if type(field) == fields.TranslatedCharField:
                all_t = getattr(self, f"{field.name}_tsall")
                self.translations[field.name] = all_t

    def __getattribute__(self, name):
        # Maybe cahce the ranslated fields, and just do funkiness on those.
        wants_all_translations = False
        if name.endswith("_tsall"):
            name = name[:-6]
            wants_all_translations = True

        attr = object.__getattribute__(self, name)
        if name.startswith('__') or name == "_meta":
            return attr
        try:
            field = self._meta.get_field(name)
            if issubclass(type(field), fields.TranslatedFieldBase):
                self.translations[name] = attr
                if wants_all_translations:
                    return attr
                else:
                    return attr.get(get_current_language(), "")
        except FieldDoesNotExist:
            pass
        return attr

    def __setattr__(self, name, value):
        if name.startswith('__') or name.startswith("_"):
            return models.Model.__setattr__(self, name, value)
        try:
            field = self._meta.get_field(name)
            if issubclass(type(field), fields.TranslatedFieldBase):
                if type(value) == str:
                    all_t = (self.translations.get(name, {}) or {}).copy()
                    all_t[get_current_language()] = value
                    value = all_t
                return models.Model.__setattr__(self, name, value)
            else:
                return models.Model.__setattr__(self, name, value)
        except FieldDoesNotExist:
            pass
        return models.Model.__setattr__(self, name, value)

