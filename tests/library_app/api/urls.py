from django.urls import path
from . import views, generators

from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


app_name = "library_app_api"

schema_view = get_schema_view(
    openapi.Info(
        title="Library API",
        default_version="v1",
        description="Library API",
        license=openapi.License(name="BSD License"),
    ),
    generator_class=generators.LibrarySchemaGenerator,
    public=True,
    permission_classes=(permissions.AllowAny,),
    urlconf="library_app.api.urls",
)


urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema"),
    path("book", views.ListCreateBookAPIView.as_view(), name="list_create_book"),
    path(
        "book/<str:item_id>",
        views.RetrieveUpdateBookAPIView.as_view(),
        name="retrieve_update_book",
    ),
]
