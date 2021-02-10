from django.conf import settings
from django.contrib.admin import widgets
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.core import exceptions
from django.db.models import Model, JSONField
from django.db.models.fields.json import KeyTransform
from django.utils.translation import gettext as _
from dataclasses import make_dataclass
from functools import partial
from langcodes import Language
import logging
from typing import Callable, Dict, Union

from garnett.utils import get_current_language, get_property_name, get_languages

logger = logging.getLogger(__name__)


class TranslatedStr(str):
    def __new__(cls, content, fallback=False, fallback_language=""):
        instance = super().__new__(cls, content)
        instance.is_fallback = fallback
        instance.fallback_language = fallback_language
        return instance


def translation_fallback(field: "TranslatedField", obj: Model) -> str:
    """Default fallback function that returns an error message"""
    all_ts = getattr(obj, f"{field.name}_tsall")
    language = get_current_language()
    lang_name = Language.make(language=language).display_name(language)
    lang_en_name = Language.make(language=language).display_name()

    return all_ts.get(
        language,
        _(
            "No translation of %(field)s available in %(lang_name)s"
            " [%(lang_en_name)s]."
        )
        % {
            "field": field.name,
            "lang_name": lang_name,
            "lang_en_name": lang_en_name,
        },
    )


def next_language_fallback(field: "TranslatedField", obj: Model) -> TranslatedStr:
    """Fallback that checks each language consecutively"""
    all_ts = getattr(obj, f"{field.name}_tsall")
    for lang in get_languages():
        if lang in all_ts:
            return TranslatedStr(all_ts[lang], fallback=True, fallback_language=lang)

    return TranslatedStr("", fallback=True)


def blank_fallback(field, obj):
    return ""


def validate_translation_dict(all_ts: dict) -> None:
    """Validate that translation dict maps valid lang code to string

    Could be used as model or form validator
    """
    if not isinstance(all_ts, dict):
        raise exceptions.ValidationError("Invalid value assigned to translatable field")

    # Check language codes
    languages = set(get_languages())
    for code, value in all_ts.items():
        if not isinstance(code, str) or code not in languages:
            raise exceptions.ValidationError(f'"{code}" is not a valid language code')

        if not isinstance(value, str):
            raise exceptions.ValidationError(f'Invalid value for language "{code}"')


def translatable_default(
    inner_default: Union[str, Callable[[], str]]
) -> Dict[str, str]:
    """Return default from inner field as dict with current language"""
    lang = get_current_language()
    if callable(inner_default):
        return {lang: inner_default()}

    return {lang: inner_default}


class TranslatedField(JSONField):
    """Translated text field that mirrors the behaviour of another text field

    All arguments except fallback can be provided on the inner field
    """

    def __init__(self, field, *args, fallback=None, **kwargs):
        self.field = field

        if fallback:
            self.fallback = fallback
        else:
            self.fallback = translation_fallback

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
        if "default" not in kwargs and (inner_default := inner_kwargs.get("default")):
            # Use partial because it is serializable in django migrations
            kwargs["default"] = partial(translatable_default, inner_default)

        super().__init__(*args, **kwargs)
        self.validators.append(validate_translation_dict)

    def formfield(self, **kwargs):
        # We need to bypass the JSONField implementation
        return self.field.formfield(**kwargs)

    def get_attname(self):
        # Use field with _tsall as the attribute name on the object
        return self.name + "_tsall"

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

        language = get_current_language()
        return all_ts.get(language, None)

    def get_attname_column(self):
        attname = self.get_attname()
        # Use name without _tsall as the column name
        column = self.db_column or self.name
        return attname, column

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        # We use ego to diferentiate scope here as this is the inner self
        # Maybe its not necessary, but it is funny

        @property
        def translator(ego):
            """Getter for main field (without _tsall)"""
            value = self.value_from_object(ego)
            if value is not None:
                return TranslatedStr(value, False)

            fallback_value = self.fallback(self, ego)
            # If fallback function didn't return a TranslatedStr wrap it in one
            if not isinstance(fallback_value, TranslatedStr):
                fallback_value = TranslatedStr(fallback_value, fallback=True)

            return fallback_value

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
                all_ts[get_current_language()] = value
            elif isinstance(value, dict):
                all_ts = value
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
            return [l for l in get_languages() if l in langs]

        setattr(cls, "available_languages", available_languages)

    def run_validators(self, values):
        # Run validators on JSON field
        # Doing this first ensures we have valid type for checks below
        super().run_validators(values)

        # Run validators on sub field
        errors = []
        for value in values.values():
            for v in self.field.validators:
                try:
                    v(value)
                except exceptions.ValidationError as e:
                    if hasattr(e, "code") and e.code in self.error_messages:
                        e.message = self.error_messages[e.code]
                    errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)

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
        kwargs["fallback"] = self.fallback
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
from garnett import lookups
