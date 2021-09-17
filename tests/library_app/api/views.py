from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from typing import Any, Dict
from library_app.models import Book
from library_app.api.serializers import BookSerializer


class ListCreateBookAPIView(generics.ListCreateAPIView):
    """The base implementation of the list and create view"""

    permission_classes = (AllowAny,)
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.all()


class RetrieveUpdateBookAPIView(generics.RetrieveUpdateAPIView):
    """The base implementation of the retrieve and update view"""

    permission_classes = (AllowAny,)
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.all()

    def get_object(self) -> Book:
        queryset = self.get_queryset()

        # Lookup by uuid or id depending on url parameters
        filters = {}
        identifier = self.kwargs["item_id"]
        if identifier.isdigit():
            filters["id"] = identifier
        else:
            raise Http404

        obj = get_object_or_404(queryset, **filters)

        # Check object against permission classes
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
