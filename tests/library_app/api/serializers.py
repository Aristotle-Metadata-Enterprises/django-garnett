from rest_framework import serializers
from library_app import models
from garnett.ext.drf import TranslatableSerializerMixin


class BookSerializer(TranslatableSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = "__all__"
