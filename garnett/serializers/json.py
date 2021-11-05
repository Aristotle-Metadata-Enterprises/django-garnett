from django.core.serializers.json import Serializer as JsonSerializer, Deserializer
from garnett.serializers.base import TranslatableSerializer


class Serializer(TranslatableSerializer, JsonSerializer):
    pass
