from django.views.generic import DetailView, ListView
from library_app.models import Book


class BookView(DetailView):
    pk_url_kwarg = "book"
    model = Book


class BookListView(ListView):
    model = Book
