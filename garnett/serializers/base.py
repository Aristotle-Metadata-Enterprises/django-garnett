from django.core.serializers.base import Serializer as BaseSerializer
from django.utils.encoding import is_protected_type
from garnett.fields import TranslatedField


def crazy(queryset):
    a = iter(queryset)

    item = next(a)

    def second_inner():
        yield item
        for t in a:
            yield t

    b = second_inner()
    return item, b


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
        """
        Serialize a queryset.
        """
        self.options = options

        self.stream = stream if stream is not None else self.stream_class()
        self.selected_fields = fields
        self.use_natural_foreign_keys = use_natural_foreign_keys
        self.use_natural_primary_keys = use_natural_primary_keys
        progress_bar = self.progress_class(progress_output, object_count)

        self.start_serialization()
        self.first = True
        for count, obj in enumerate(queryset, start=1):
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            # When using natural primary keys, retrieve the pk field of the
            # parent for multi-table inheritance child models. That field must
            # be serialized, otherwise deserialization isn't possible.
            if self.use_natural_primary_keys:
                pk = concrete_model._meta.pk
                pk_parent = (
                    pk if pk.remote_field and pk.remote_field.parent_link else None
                )
            else:
                pk_parent = None
            for field in concrete_model._meta.local_fields:
                if field.serialize or field is pk_parent:
                    # ------------
                    if isinstance(field, TranslatedField):
                        if (
                            self.selected_fields is None
                            or field.name in self.selected_fields
                        ):
                            self.handle_field(obj, field)
                    # ----------------------
                    elif field.remote_field is None:
                        if (
                            self.selected_fields is None
                            or field.attname in self.selected_fields
                        ):
                            self.handle_field(obj, field)
                    else:
                        if (
                            self.selected_fields is None
                            or field.attname[:-3] in self.selected_fields
                        ):
                            self.handle_fk_field(obj, field)
            for field in concrete_model._meta.local_many_to_many:
                if field.serialize:
                    if (
                        self.selected_fields is None
                        or field.attname in self.selected_fields
                    ):
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
            progress_bar.update(count)
            self.first = self.first and False
        self.end_serialization()
        return self.getvalue()

    def _serialize(
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
            item, queryset = crazy(queryset)
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
