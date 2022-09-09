"""library_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from library_app import views

urlpatterns = [
    path("", views.BookListView.as_view()),
    path("api/", include("library_app.api.urls", namespace="library_app_api")),
    path("admin/", admin.site.urls),
    path("book/<int:book>", views.BookView.as_view()),
    path("book/<int:pk>/edit", views.BookUpdateView.as_view(), name="update_book"),
    path("book/<int:pk>/history", views.BookHistoryCompareView.as_view()),
]
