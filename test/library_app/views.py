from django.views.generic import DetailView
from library_app.models import Book


class BookView(DetailView):
    pk_url_kwarg = "book"
    template = "book.html"
    model = Book
