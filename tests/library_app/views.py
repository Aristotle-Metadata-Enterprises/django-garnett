from django.views.generic import DetailView, ListView, UpdateView
from reversion_compare.views import HistoryCompareDetailView
from garnett.utils import get_current_language_code

from library_app.models import Book


class BookView(DetailView):
    pk_url_kwarg = "book"
    model = Book


class BookListView(ListView):
    model = Book

    def get_ordering(self):
        code = get_current_language_code()
        return f"title__{code}"


class BookUpdateView(UpdateView):
    model = Book
    fields = "__all__"


class BookHistoryCompareView(HistoryCompareDetailView):
    model = Book
    template_name = "library_app/book_history.html"
