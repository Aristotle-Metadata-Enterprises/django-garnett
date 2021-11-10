from django.core.serializers.base import Serializer as BaseSerializer
from django.utils.encoding import is_protected_type
from garnett.fields import TranslatedField


def fetch_item_and_convert_to_generator(queryset):
    # This method exists so we can get the first item of an iterable
    # (which can include a generator), and then still iterate through the entire
    # set later.
    # This ensures that if we have a queryset we only fetch it once,
    # or run through the generator once.
    inner_iterable = iter(queryset)

    # Get the first item so we can do introspection
    item = next(inner_iterable)

    # Make a generator that returns the first item, then the rest of the iterable
    def inner_generator():
        yield item
        yield from inner_iterable

    return item, inner_generator()


class TranslatableSerializer(BaseSerializer):
    def serialize(
        self,
        queryset,
        *,
        stream=None,
        fields=None,
        use_natural_foreign_keys=False,
        use_natural_primary_keys=False,
        progress_output=None,
        object_count=0,
        **options
    ):

        if fields is not None:
            item, queryset = fetch_item_and_convert_to_generator(queryset)
            selected_fields = []
            for f in item._meta.fields:
                if f.name in fields:
                    if isinstance(f, TranslatedField):
                        selected_fields.append(f.attname)
                    else:
                        selected_fields.append(f.name)
            fields = selected_fields

        return super().serialize(
            queryset,
            stream=stream,
            fields=fields,
            use_natural_foreign_keys=use_natural_foreign_keys,
            use_natural_primary_keys=use_natural_primary_keys,
            progress_output=progress_output,
            object_count=object_count,
            **options
        )

    def _value_from_field(self, obj, field):
        value = field.value_from_object(obj)
        # Protected types (i.e., primitives like None, numbers, dates,
        # and Decimals) are passed through as is. All other values are
        # converted to string first.
        if isinstance(field, TranslatedField):
            return field.translations_from_object(obj)
        return value if is_protected_type(value) else field.value_to_string(obj)
