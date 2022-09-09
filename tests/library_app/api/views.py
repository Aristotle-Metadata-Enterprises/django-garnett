from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import generics
from django.http import Http404
from django.shortcuts import get_object_or_404
from library_app.models import Book
from library_app.api.serializers import BookSerializer
from django_filters.rest_framework import DjangoFilterBackend


class ListCreateBookAPIView(generics.ListCreateAPIView):
    """The base implementation of the list and create view"""

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title", "author"]

    def get_queryset(self):
        return Book.objects.all()


class RetrieveUpdateBookAPIView(generics.RetrieveUpdateAPIView):
    """The base implementation of the retrieve and update view"""

    permission_classes = (IsAuthenticated,)
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
