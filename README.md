# django-garnett

Django Garnett is a field level translation library that allows you to store strings in multiple languages for fields in Django - with minimal changes to your models and without having to rewrite your code.

Want a demo? https://django-garnett.herokuapp.com/

<a href="https://www.aristotlemetadata.com"
    style="text-decoration: none">
Made with <i style="color:#d63384">♥</i> by
<img src="https://brand.aristotlemetadata.com/images/svgs/thick.svg" height=20> Aristotle Metadata
</a>

In summary it allows you to do this:

<table>
<tr>
    <td>
        <tt>models.py</tt>
    <td>
        You can do this!
</tr>
<tr>
<td>
By changing your models from this...

```python
class Greeting(models.model):
    text = CharField(max_length=150)
    target = models.CharField()
    def __str__(self):
        return f"{self.greeting}, {self.target}"

```

to this...

```python
# Import garnett
from garnett.fields import Translated

class Greeting(models.model):
    # Convert greeting to a translatable field
    text = Translated(CharField(max_length=150))
    target = models.CharField()
    def __str__(self):
        return f"{self.greeting} {self.target}"
```
</td>
<td>

```python
greeting = Greeting(text="Hello", target="World")

with set_field_language("en"):
    greeting.text = "Hello"
with set_field_language("fr"):
    greeting.text = "Bonjour"

greeting.save()
greeting.refresh_from_db()

with set_field_language("en"):
    print(greeting.text)
    print(greeting)
# >>> "Hello"
# >>> "Hello World"

with set_field_language("fr"):
    print(greeting.text)
    print(greeting)
# >>> "Bonjour"
# >>> "Bonjour World!"

with set_field_language("en"):
    print(greeting.text)
    print(greeting)
# >>> "Hello"
# >>> "Hello World"
    Greeting.objects.filter(title="Hello").exists()
# >>> True
    Greeting.objects.filter(title="Bonjour").exists()
# >>> False
    Greeting.objects.filter(title__fr="Bonjour").exists()
# >>> True!!

# Assuming that GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE="en"
# Or a middleware has set the language context
print(greeting.text)
# >>> Hello
print(greeting)
# >>> Hello World!

```

</td>
</table>

Tested on:

  - Django 3.1+
  - Postgres, SQLite, MariaDB
  - Python 3.7+


Pros:
* Fetching all translations for a models requires a single query
* Translations are stored in a single database field with the model
* Translations act like regular a field `Model.field_name = "some string"` and `print(Model.field_name)` work as you would expect
* Includes a configurable middleware that can set the current language context based on users cookies, query string or HTTP headers
* Works nicely with Django Rest Framework

Cons:
* You need to alter the models, so you can't make third-party libraries translatable.

## Why write a new Django field translator?

A few reasons:
* Most existing django field translation libraries are static, and add separate database columns per translation.
* We needed a library that could be added in without requiring a rewrite of a very large code base.

Note: Field language is different to the django display language. Django can be set up to translate your pages based on the users browser and serve them with a user interface in their preferred language.

Garnett *does not* use the browser language by design - a user with a French browser may want the user interface in French, but want to see content in English.


# How to install

1. Add `django-garnett` to your dependencies. eg. `pip install django-garnett`
2. Convert your chosen field using the `Translated` function

    * For example: `title = fields.Translated(models.CharField(*args))`

3. Add `GARNETT_TRANSLATABLE_LANGUAGES` (a callable or list of [language codes][term-language-code]) to your django settings.
    > Note: At the moment there is no way to allow "a user to enter any language".
4. Add `GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE` (a callable or single [language code][term-language-code]) to your settings.
5. Re-run `django makemigrations` & `django migrate` for any apps you've updated.
6. Thats mostly it.

You can also add a few optional value adds:

7. (Optional) Add a garnett middleware to take care of field language handling:

    * You want to capture the garnett language in a context variable available in views use: `garnett.middleware.TranslationContextMiddleware`

    * You want to capture the garnett language in a context variable available in views, and want to raise a 404 if the user requests an invalid language use: `garnett.middleware.TranslationContextNotFoundMiddleware`

    * (Future addition) You want to capture the garnett language in a context variable available in views, and want to redirect to the default language if the user requests an invalid language use: `garnett.middleware.TranslationContextRedirectDefaultMiddleware`

    * If you want to cache the current language in session storage use `garnett.middleware.TranslationCacheMiddleware` after one of the above middleware (this is useful with the session selector mentioned below)

8. (Optional) Add the `garnett` app to your `INSTALLED_APPS` to use garnett's template_tags. If this is installed before `django.contrib.admin` it also include a language switcher in the Django Admin Site.

9. (Optional) Add a template processor:

    * Install `garnett.context_processors.languages` this will add `garnett_languages` (a list of available `Language`s) and `garnett_current_language` (the currently selected language).

10. (Optional) Add a custom translation fallback:

    By default, if a language isn't available for a field, Garnett will show a mesage like:
    > No translation of this field available in English

    You can override this either by creating a custom fallback method:
    ```
    Translated(CharField(max_length=150), fallback=my_fallback_method))
    ```
    Where `my_fallback_method` takes a dictionary of language codes and corresponding strings, and returns the necessary text.

    Additionally, you can customise how django outputs text in templates by creating a new
    `TranslationStr` class, and overriding the [`__html__` method][dunder-html].



## `Language` vs language

Django Garnett uses the python `langcodes` library to determine more information about the languages being used - including the full name and local name of the language being used. This is stored as a `Language` object.


## Django Settings options:

* `GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE`
    * Stores the default language to be used for reading and writing fields if no language is set in a context manager or by a request.
    * By default it is 'en-AU' the [language code][term-language-code] for 'Strayan, the native tongue of inhabitants of 'Straya (or more commonly known as Australia). 
    * Can also be callable that returns default language code
    * default: `'en-AU'`
* `GARNETT_TRANSLATABLE_LANGUAGES`:
    * Stores a list of [language codes][term-language-code] that users can use to save against TranslatableFields.
    * Can also be callable that returns list of language codes
    * default `[GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE]`
* `GARNETT_REQUEST_LANGUAGE_SELECTORS`:
    * A list of string modules that determines the order of options used to determine the language selected by the user. The first selector found is used for the language for the request, if none are found the DEFAULT_LANGUAGE is used. These can any of the following in any order:
        * `garnett.selector.query`: Checks the `GARNETT_QUERY_PARAMETER_NAME` for a language to display
        * `garnett.selector.cookie`: Checks for a cookie called `GARNETT_LANGUAGE_CODE` for a language to display.
            Note: you cannot change this cookie name.
        * `garnett.selector.session`: Checks for a session key `GARNETT_LANGUAGE_CODE` for a language to display.
            Note: you cannot change this key name.
        * `garnett.selector.header`: Checks for a HTTP Header called `X-Garnett-Language-Code` for a language to display.
            Note: you cannot change this Header name.
        * `garnett.selector.browser`: Uses Django's `get_language` function to get the users browser/UI language [as determined by Django][django-how].
    * For example, if you only want to check headers and cookies in that order, set this to `['garnett.selector.header', 'garnett.selector.cookie']`.
    * default: `['garnett.selector.query', 'garnett.selector.cookie', 'garnett.selector.header']`
* `GARNETT_QUERY_PARAMETER_NAME`:
    * The query parameter used to determine the language requested by a user during a HTTP request.
    * default: `glang`

Advanced Settings (you probably don't need to adjust these)
* `GARNETT_TRANSLATABLE_FIELDS_PROPERTY_NAME`:
    * Garnett adds a property to all models that returns a list of all TranslatableFields. By default, this is 'translatable_fields', but you can customise it here if you want.
    * default: `translatable_fields`
* `GARNETT_TRANSLATIONS_PROPERTY_NAME`:
    * Garnett adds a property to all models that returns a dictionary of all translations of all TranslatableFields. By default, this is 'translations', but you can customise it here if you want.
    * default: `translations`


## Why call it Garnett?

* Libraries need a good name.
* Searching for "Famous Translators" will tell you about [Constance Garnett](https://en.wikipedia.org/wiki/Constance_Garnett).
* Searching for "Django Garnett" showed there was no python library with this name.
* It did however talk about [Garnet Clark](https://en.wikipedia.org/wiki/Garnet_Clark) (also spelled Garnett), a jazz pianist who played with Django Reinhart - the namesake of the Django Web Framework.
* Voila - a nice name

## Warnings

* `contains == icontains` - On SQLite only, when doing a contains query
 it does a case insensitive search. I don't know why - https://www.youtube.com/watch?v=PgGNWRtceag
* Due to how django sets admin form fields you will not get the admin specific widgets like
  `AdminTextAreaWidget` on translated fields in the django admin site by default. They can however
  be specified explicitly on the corresponding admin model form.

need to run tests like this for now: PYTHONPATH=../ ./manage.py shell

[term-language-code]: https://docs.djangoproject.com/en/3.1/topics/i18n/#term-language-code
[django-how]: https://docs.djangoproject.com/en/3.1/topics/i18n/translation/#how-django-discovers-language-preference
[dunder-html]: https://code.djangoproject.com/ticket/7261