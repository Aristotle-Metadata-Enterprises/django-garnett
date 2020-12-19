from django.db import models
from garnett import fields
from garnett.models import Translatable


class Book(models.Model):
    number_of_pages = models.PositiveIntegerField()
    title = fields.TranslatedCharField()
    description = fields.TranslatedTextField()

    def get_absolute_url(self):
        return f"/book/{self.pk}"
