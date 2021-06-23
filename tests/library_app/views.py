from django.views.generic import DetailView, ListView
from library_app.models import Book
from garnett.utils import get_current_language_code


class BookView(DetailView):
    pk_url_kwarg = "book"
    model = Book


class BookListView(ListView):
    model = Book

    def get_ordering(self):
        code = get_current_language_code()
        return f"title__{code}"
