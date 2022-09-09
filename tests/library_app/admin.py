from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin
from library_app.models import Book
import reversion

reversion.register(Book)


class BookAdmin(CompareVersionAdmin):
    pass


admin.site.register(Book, BookAdmin)
