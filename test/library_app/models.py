from django.db import models
from garnett import fields
from garnett.utils import get_current_language


class Book(models.Model):
    number_of_pages = models.PositiveIntegerField()
    title = fields.TranslatedCharField()
    author = models.TextField()
    description = fields.TranslatedTextField()
    category = models.JSONField()

    def get_absolute_url(self):
        return f"/book/{self.pk}"

    def __str__(self):
        if self.title:
            print(type(self.title))
            # print(type(self.title.value))
            print(self.title)
            return self.title
        else:
            current_lang = get_current_language()
            lang, value = list(self.translations.title.items())[0]
            return f"{value} (Book title unavailable in {current_lang}, falling back to {lang})"
        # return  _(
        #             "No translation of %(field)s available in %(lang_name)s"
        #             " [%(lang_en_name)s]."
        #         ) % {
        #             'field': name,
        #             'lang_name': lang_name,
        #             'lang_en_name': lang_en_name,
        #         }
        # return self.title
