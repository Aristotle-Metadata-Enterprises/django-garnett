from django.test import TestCase
from .test_modelforms import BookFormTestBase


class AdminBookFormTests(BookFormTestBase, TestCase):
    url_name = "admin:library_app_book_change"
