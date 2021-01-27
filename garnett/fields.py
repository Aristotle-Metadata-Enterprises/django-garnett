from django.conf import settings
from django.contrib.admin import widgets
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.core import exceptions
from django.db.models import CharField, JSONField, TextField
from django.db.models.fields.json import KeyTransform
from django.utils.translation import gettext as _
from dataclasses import make_dataclass
from langcodes import Language
import logging

from garnett.utils import get_current_language, get_property_name, get_languages

logger = logging.getLogger(__name__)


class TranslationFieldError(Exception):
    """Base class for translation field errors"""

    def __init__(self, message):
        self.message = message


def translation_fallback(field, obj):
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


def blank_fallback(field, obj):
    return ""


def validate_translation_dict(all_ts):
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


class TranslatedField(JSONField):
    # Field to represent data stored for each language
    base_field = CharField
    # Kwargs to move though to base field
    kwargs_to_move = []

    def __init__(self, *args, fallback=None, **kwargs):
        base_field_kwargs = {}
        for k in self.kwargs_to_move:
            if v := kwargs.pop(k, None):
                base_field_kwargs[k] = v
        self.field = self.base_field(**base_field_kwargs)

        if fallback:
            self.fallback = fallback
        else:
            self.fallback = translation_fallback

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
                return value

            return self.fallback(self, ego)

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
                if isinstance(field, TranslatedFieldBase)
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


class TranslatedKeyTransform(KeyTransform):
    """Key transform for translate fields

    so we can register lookups on this without affecting the regular json field
    """


class TranslatedKeyTransformFactory:
    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return TranslatedKeyTransform(self.key_name, *args, **kwargs)


class TranslatedCharField(TranslatedField):
    base_field = CharField
    kwargs_to_move = ["validators", "max_length"]


class TranslatedTextField(TranslatedField):
    base_field = TextField
    kwargs_to_move = ["validators"]


# Import lookups here so that they are registered by just importing the field
from garnett import lookups


# Add widget for django admin
FORMFIELD_FOR_DBFIELD_DEFAULTS.update(
    {
        TranslatedTextField: {"widget": widgets.AdminTextareaWidget},
    }
)
