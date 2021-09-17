from django.conf import settings
from django.core import exceptions
from django.db.models import JSONField
from django.db.models.fields.json import KeyTransform
from dataclasses import make_dataclass
from functools import partial
import logging
from typing import Callable, Dict, Union

from garnett.translatedstr import TranslatedStr, VerboseTranslatedStr
from garnett.utils import (
    get_current_language_code,
    get_property_name,
    get_languages,
    is_valid_language,
    normalise_language_codes,
)

logger = logging.getLogger(__name__)


def innerfield_validator_factory(innerfield) -> callable:
    def validator(values: dict):
        if not isinstance(values, dict):
            raise exceptions.ValidationError(
                "Invalid value assigned to translatable field"
            )

        # Run validators on sub field
        errors = []
        for code, value in values.items():
            # Check language codes
            if not isinstance(value, str):
                raise exceptions.ValidationError(f'Invalid value for language "{code}"')
            if not is_valid_language(code):
                raise exceptions.ValidationError(
                    f'"{code}" is not a valid language code'
                )

            for v in innerfield.validators:
                try:
                    v(value)
                except exceptions.ValidationError as e:
                    errors.extend(e.error_list)
        if errors:
            raise exceptions.ValidationError(errors)

    return validator


def translatable_default(
    inner_default: Union[str, Callable[[], str]]
) -> Dict[str, str]:
    """Return default from inner field as dict with current language"""
    lang = get_current_language_code()
    if callable(inner_default):
        return {lang: inner_default()}

    return {lang: inner_default}


class TranslatedField(JSONField):
    """Translated text field that mirrors the behaviour of another text field

    All arguments except fallback can be provided on the inner field
    """

    def __init__(self, field, *args, fallback=None, **kwargs):
        self.field = field
        self._fallback = fallback

        if type(fallback) is type and issubclass(fallback, TranslatedStr):
            self.fallback = fallback
        elif callable(fallback):
            self.fallback = partial(TranslatedStr, fallback=fallback)
        else:
            self.fallback = VerboseTranslatedStr

        # Move some args to outer field
        outer_args = [
            "db_column",
            "db_index",
            "db_tablespace",
            "help_text",
            "verbose_name",
        ]
        inner_kwargs = self.field.deconstruct()[3]
        for arg_name in outer_args:
            if arg_name in inner_kwargs:
                kwargs[arg_name] = inner_kwargs[arg_name]

        # Create default for outer field based on inner field
        if "default" not in kwargs and "default" in inner_kwargs:
            # Use partial because it is serializable in django migrations
            kwargs["default"] = partial(translatable_default, inner_kwargs["default"])

        super().__init__(*args, **kwargs)
        self.validators.append(innerfield_validator_factory(self.field))

    def formfield(self, **kwargs):
        # We need to bypass the JSONField implementation
        return self.field.formfield(**kwargs)

    def get_attname(self):
        # Use field with _tsall as the attribute name on the object
        return self.name + "_tsall"

    def get_prep_value(self, value):
        if hasattr(value, "items"):
            value = {
                lang_code: self.field.get_prep_value(text)
                for lang_code, text in value.items()
            }
        elif type(value) == str:
            value = self.field.get_prep_value(value)
            return value
        return super().get_prep_value(value)

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        if hasattr(self.field, "from_db_value"):
            value = {
                k: self.field.from_db_value(v, expression, connection)
                for k, v in value.items()
            }
        return value

    def value_from_object(self, obj):
        """Return the value of this field in the given model instance."""
        all_ts = getattr(obj, f"{self.name}_tsall")
        if type(all_ts) is not dict:
            logger.warning(
                "Displaying an untranslatable field - model:{} (pk:{}), field:{}".format(
                    type(obj), obj.pk, self.name
                )
            )
            return str(all_ts)

        language = get_current_language_code()
        return all_ts.get(language, None)

    def get_attname_column(self):
        attname = self.get_attname()
        # Use name without _tsall as the column name
        column = self.db_column or self.name
        return attname, column

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        # We use `ego` to differentiate scope here as this is the inner self
        # Maybe its not necessary, but it is funny.

        @property
        def translator(ego):
            return self.fallback(getattr(ego, f"{self.name}_tsall"))

        @translator.setter
        def translator(ego, value):
            """Setter for main field (without _tsall)"""
            all_ts = getattr(ego, f"{name}_tsall")
            if not all_ts:
                # This is probably the first save through
                all_ts = {}
            elif type(all_ts) is not dict:
                logger.warning(
                    "Saving a broken field - model:{} (pk:{}), field:{}".format(
                        type(ego), ego.pk, name
                    )
                )
                logger.debug("Field data was - {}".format(all_ts))
                all_ts = {}

            if isinstance(value, str):
                language_code = get_current_language_code()
                all_ts[language_code] = value
            elif isinstance(value, dict):
                # normalise all language codes
                all_ts = normalise_language_codes(value)
            else:
                raise TypeError("Invalid type assigned to translatable field")

            setattr(ego, f"{name}_tsall", all_ts)

        setattr(cls, f"{name}", translator)

        # This can probably be cached on the class
        @property
        def translatable_fields(ego):
            return [
                field
                for field in ego._meta.get_fields()
                if isinstance(field, TranslatedField)
            ]

        propname = getattr(
            settings, "GARNETT_TRANSLATABLE_FIELDS_PROPERTY_NAME", "translatable_fields"
        )
        setattr(cls, propname, translatable_fields)

        @property
        def translations(ego):
            translatable_fields = ego.translatable_fields
            Translations = make_dataclass(
                "Translations", [(f.name, dict) for f in translatable_fields]
            )
            kwargs = {}
            for field in translatable_fields:
                kwargs[field.name] = getattr(ego, f"{field.name}_tsall")
            return Translations(**kwargs)

        setattr(cls, get_property_name(), translations)

        @property
        def available_languages(ego):
            """Returns a list of codes available on the whole model"""
            langs = set()
            for field in ego.translatable_fields:
                langs |= getattr(ego, f"{field.name}_tsall", {}).keys()
            return [lang for lang in get_languages() if lang.language in langs]

        setattr(cls, "available_languages", available_languages)

    def get_transform(self, name):
        # Call back to the Field get_transform
        transform = super(JSONField, self).get_transform(name)
        if transform:
            return transform
        # Use our new factory
        return TranslatedKeyTransformFactory(name)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        args.insert(0, self.field)
        kwargs["fallback"] = self._fallback
        return name, path, args, kwargs


class TranslatedKeyTransform(KeyTransform):
    """Key transform for translate fields

    so we can register lookups on this without affecting the regular json field
    """


class TranslatedKeyTransformFactory:
    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return TranslatedKeyTransform(self.key_name, *args, **kwargs)


# Shorter name for the class
Translated = TranslatedField


# Import lookups here so that they are registered by just importing the field
from garnett import lookups  # noqa: F401, E402
