# django-garnett

need to run tests like this for now: PYTHONPATH=../ ./manage.py shell

## Why write a new Django field translator?

A few reasons:
* Most existing django field translation libraries are static, and add separate database columns per translation.
* We needed a library that could be added in without requiring a rewrite of a large code base.

Note: Field language is different to the django display langauge. Django can be set up to translate your pages based on the users browser and serve them with a user interface in their preferred language.

Garnett *does not* use the browser language by design - a user with a French browser may want the user interface in French, but want to see content in English.

# How to install

1. Add `django-garnett` to your dependencies. eg. `pip install django-garnett`
2. Convert your chosen field to a `TranslatedCharField`

    * For example: `title = fields.TranslatedCharField(*args)`

3. Add `GARNETT_TRANSLATABLE_LANGUAGES` (a callable or list of language codes) to your django settings.
    > In future make optional, if this isn't set, then users can enter any language they want.
4. Add `GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE` (a single language code) to your settings.
5. Re-run `django makemigrations` & `django migrate` for any apps you've updated.
6. Thats mostly it.

You can also add a few value adds:

7. (Optional) Add a garnett middleware to take care of field language handling:

    * You want to capture the garnett language in a context variable available in views use: `garnett.middleware.TranslationContextMiddleware`

    * You want to capture the garnett language in a context variable available in views, and want to raise a 404 if the user requests an invalid language use: `garnett.middleware.TranslationContextNotFoundMiddleware`

    * (Future addition) You want to capture the garnett language in a context variable available in views, and want to redirect to the default language if the user requests an invalid language use: `garnett.middleware.TranslationContextRedirectDefaultMiddleware`

8. (Optional) Add the `garnett` app to your `INSTALLED_APPS` to use garnett's template_tags. If this is installed before `django.contrib.admin` it also include a languge switcher in the Django Admin Site.

9. (Optional) Add a template processor:

    * Install `garnett.context_processors.languages` this will add `garnett_languages` (a list of available `Language`s) and `garnett_current_language` (the currently selected language).

## `Language` vs language

Django Garnett uses the python `langcodes` to determine more information about the languages being used - including the full name and local name of the language being used.


## Django Settings options:

* `GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE`
    * Stores the default language to be used for reading and writing fields if no language is set in a context manager or by a request.
    * By default it is 'en-AU' the language code for 'Strayan, the native tongue of inhabitants of 'Straya (or more commonly known as Australia). 
    * default: `'en-AU'`
* `GARNETT_TRANSLATABLE_LANGUAGES`:
    * Stores a list of language codes that users can use to save against TranslatableFields.
    * default [GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE]
* `GARNETT_REQUEST_LANGUAGE_SELECTORS`:
    * Determines the order of options used to determine the language selected by the user. The first selector found is used for the language for the request, if none are found the DEFAULT_LANGUAGE is used. These can any of the following in any order:
        * "query": Checks the `GARNETT_QUERY_PARAMATER_NAME` for a language to display
        * "cookie": Checks for a cookie called "GARNETT_LANGUAGE_CODE" for a language to display.
            Note: you cannot change this cookie name.
        * "header": Checks for a HTTP Header called "X-Garnett-Language-Code" for a language to display.
            Note: you cannot change this Header name.
    * For example, if you only want to check headers and cookies in that order, set this to `['header', 'cookie']`.
    * default: `['query', 'cookie', 'header']`
* `GARNETT_QUERY_PARAMATER_NAME`:
    * The query parameter used to determine the language requested by a user during a HTTP request.
    * default: `glang`

Advanced Settings (you probably neither need or want to change these)
* `GARNETT_TRANSLATABLE_FIELDS_PROPERTY_NAME`:
    * Garnett adds a property to all models that returns a list of all TranslatableFields. By default, this is 'translatable_fields', but you can customise it here if yoou want.
    * default: `translatable_fields`
* `GARNETT_TRANSLATIONS_PROPERTY_NAME`:
    * Garnett adds a property to all models that returns a dictionary of all translations of all TranslatableFields. By default, this is 'translations', but you can customise it here if yoou want.    * default: `translations`



## Why call it Garnett?

* Libraries need a good name.
* Searching for "Famous Translators" will tell you about [Constnace Garnett](https://en.wikipedia.org/wiki/Constance_Garnett).
* Searching for "Garnett Django" shows there was no library with this name. It did however talk about [Garnet Clark](https://en.wikipedia.org/wiki/Garnet_Clark) (also spelled Garnett), a jazz pianist who played with Django Reinhart - the namesake of the Django Web Framework.
* Voila - a nice name

## Warnings

* `contains == icontains` For cross database compatibility reasons this library treats `contains` like `icontains`. I don't know why - https://www.youtube.com/watch?v=PgGNWRtceag

TODOs:
* [x] Add a custom lookups that handle `Translatable` fields, eg. if a user does `Book.objects.filter(name__icontains="thing")` filters operate on the current language only
* [x] Add lots of tests!
  - [x] Tests for validators

* [ ] Verify data going into the database is a dictionary with string keys and string values, eg. `{"lang-code-1": "value", "lang-code-2": "value"}`
* [x] Move getter and setter to `Field.contribute_to_class`
* [ ] Test how this works with DRF
* [x] Test postgres search fields
* [ ] Have TranslatableField take the original CharField as an argument. eg:
    - `Translatable( (CharField(...args), fallback=func )`
    - `Translatable( (TextField(...args), fallback=func )`
* [ ] Add: `TranslationContextRedirectDefaultMiddleware`
* [ ] Check F strings and Expressions