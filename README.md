# django-garnett

need to run tests like this for now: PYTHONPATH=../ ./manage.py shell

## Why write a new Django field translator?

A few reasons:
* Most existing django field translation libraries are static, and add separate database columns per translation.
* We needed a library that could be added in without requiring a rewrite of a large code base.

Note: Field language is different to the django display langauge. Django can be set up to translate your pages based on the users browser and serve them with a user interface in their preferred language.

Garnett *does not* use the browser language by design - a user with a French browser may want the user interface in French, but want to see content in English.

# How to install

1. Add `django-garnett` to you dependencies. eg. `pip install django-garnett`
2. Convert your chosen field to a `TranslatedCharField`

    * For example: `title = fields.TranslatedCharField(*args)`

3. Add `GARNETT_TRANSLATABLE_LANGUAGES` (a callable or list of language codes) to your django settings.
    > In future make optional, if this isn't set, then users can enter any language they want.
4. Add `GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE` (a single language code) to your settings.
    > In future make optional, if this isn't set
5. Re-run `django makemigrations` for your app.
6. Thats mostly it.

You can also add a few value adds:

7. (Optional) Add a garnett middleware to take care of field language handling:

    * You want to capture the garnett language in a context variable available in views use: `garnett.middleware.TranslationContextMiddleware`

    * You want to capture the garnett language in a context variable available in views, and want to raise a 404 if the user requests an invalid language use: `garnett.middleware.TranslationContextNotFoundMiddleware`

    * (Future) You want to capture the garnett language in a context variable available in views, and want to redirect to the default language if the user requests an invalid language use: `garnett.middleware.TranslationContextRedirectMiddleware`

7. (Optional) Add a template processor:

    * Install `garnett.context_processors.languages` this will add `garnett_languages` (a list of available `Language`s) and `garnett_current_language` (the currently selected language).

## `Language` vs language

Django Garnett uses the python `langcodes` to determine more information about the languages being used - including the full name and local name of the language being used.


## Why call it Garnett?

* Libraries need a good name.
* Searching for "Famous Translators" will tell you about [Constnace Garnett](https://en.wikipedia.org/wiki/Constance_Garnett), a famous translator.
* Searching for "Garnett Django" shows [Garnet Clark](https://en.wikipedia.org/wiki/Garnet_Clark), a jazz pianist who played with Django Reinhart - the namesake of the Django Web Framework.


TODOs:
* Add a custom lookups that handle `Translatable` fields, eg. if a user does `Book.objects.filter(name__icontains="thing")` filters operate on the current language only
* Add lots of tests!
* Verify data going into the database is a dictionary with string keys and string values, eg. `{"lang-code-1": "value", "lang-code-2": "value"}`
* Move getter and setter to `Field.contribute_to_class`
* Test how this works with DRF