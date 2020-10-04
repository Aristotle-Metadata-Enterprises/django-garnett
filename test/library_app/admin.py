from django.contrib import admin
from library_app.models import Book

class BookAdmin(admin.ModelAdmin):
    pass

admin.site.register(Book, BookAdmin)