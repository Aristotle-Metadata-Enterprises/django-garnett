from django.core.serializers import json
from garnett.serializers.base import TranslatableSerializer


class Serializer(TranslatableSerializer, json.Serializer):
    pass


def Deserializer(stream_or_string, **options):
    yield from json.Deserializer(stream_or_string, **options)
