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
from garnett.context import set_field_language
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

Tested with the following libraries:
  - [Django Rest Framework](https://www.django-rest-framework.org/)
  - [django-reversion](https://github.com/etianen/django-reversion) & [django-reversion-compare](https://github.com/jedie/django-reversion-compare)
  - [django-filters](https://github.com/carltongibson/django-filter)

Pros:
* Battletested in production - [Aristotle Metadata](https://www.aristotlemetadata.com) built, support and uses this library for 2 separate products, served to government and enterprise clients!
* Fetching all translations for a model requires a single query
* Translations are stored in a single database field with the model
* All translations act like a regular field, so `Model.field_name = "some string"` and `print(Model.field_name)` work as you would expect
* Includes a configurable middleware that can set the current language context based on users cookies, query string or HTTP headers
* Works nicely with Django Rest Framework - translatable fields can be set as strings or as json dictionaries
* Works nicely with Django `F()` and `Q()` objects within the ORM - and when it doesn't we have a language aware `LangF()` replacement you can use.

Cons:
* You need to alter the models, so you can't make third-party libraries translatable.
* It doesn't work on `queryset.values_list` - but we have a workaround below.

## Why write a new Django field translator?

A few reasons:
* Most existing django field translation libraries are static, and add separate database columns or extra tables per translation.
* Other libraries may not be compatible with common django libraries, like django-rest-framework.
* We had a huge codebase that we wanted to upgrade to be multilingual - so we needed a library that could be added in without requiring a rewriting every access to fields on models, and only required minor tweaks.

Note: Field language is different to the django display language. Django can be set up to translate your pages based on the users browser and serve them with a user interface in their preferred language.

Garnett *does not* use the browser language by design - a user with a French browser may want the user interface in French, but want to see content in English or French based on their needs.


# How to install

1. Add `django-garnett` to your dependencies. eg. `pip install django-garnett`
2. Convert your chosen field using the `Translated` function

    * For example: `title = fields.Translated(models.CharField(*args))`

3. Add `GARNETT_TRANSLATABLE_LANGUAGES` (a callable or list of [language codes][term-language-code]) to your django settings.
    > Note: At the moment there is no way to allow "a user to enter any language".
4. Add `GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE` (a callable or single [language code][term-language-code]) to your settings.
5. Re-run `django makemigrations`, perform a data migration to make your existing data translatable (See 'Data migrations') & `django migrate` for any apps you've updated.
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


## Data migrations

If you have lots of existing data (and if you are using this library you probably do) you will need to perform data migrations to make sure all of your existing data is multi-lingual aware. Fortunately, we've added some well tested migration utilities that can take care of this for you.

Once you have run `django-admin makemigrations` you just need to add the `step_1_safe_encode_content` before and `step_2_safe_prepare_translations` after your schema migrations, like in the following example:

```python
# Generated by Django 3.1.13 on 2022-01-11 10:13

from django.db import migrations, models
import garnett.fields
import library_app.models

#### Add this line in 
from garnett.migrate import step_1_safe_encode_content, step_2_safe_prepare_translations

#### Define the models and fields you want ot migrate
model_fields = {
    "book": ["title", "description"],
}


class Migration(migrations.Migration):

    dependencies = [
        ("library_app", "0001_initial"),
    ]

    operations = [
        ## Add this operation at the start
        step_1_safe_encode_content("library_app", model_fields),

        ## These are the automatically generated migrations
        migrations.AlterField(  # ... migrate title to TranslatedField),
        migrations.AlterField(  # ... migrate description to TranslatedField),

        ## Add this operation at the start
        step_2_safe_prepare_translations("library_app", model_fields),
    ]

```


## `Language` vs language

Django Garnett uses the python `langcodes` library to determine more information about the languages being used - including the full name and local name of the language being used. This is stored as a `Language` object.


## Django Settings options:

* `GARNETT_DEFAULT_TRANSLATABLE_LANGUAGE`
    * Stores the default language to be used for reading and writing fields if no language is set in a context manager or by a request.
    * By default it is 'en-AU' the [language code][term-language-code] for 'Strayan, the native tongue of inhabitants of 'Straya (or more commonly known as Australia). 
    * This can also be a callable that returns list of language codes. Combined with storing user settings in something like (django-solo)[https://github.com/lazybird/django-solo] users can dynamically add or change their language settings.
    * default: `'en-AU'`
* `GARNETT_TRANSLATABLE_LANGUAGES`:
    * Stores a list of [language codes][term-language-code] that users can use to save against TranslatableFields.
    * This can also be a callable that returns list of language codes. Combined with storing user settings in something like (django-solo)[https://github.com/lazybird/django-solo] users can dynamically add or change their language settings.
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
    * For example, if you only want to check headers and cookies in that order, set this to `['garnett.selectors.header', 'garnett.selectors.cookie']`.
    * default: `['garnett.selectors.header', 'garnett.selectors.query', 'garnett.selectors.cookie']`
* `GARNETT_QUERY_PARAMETER_NAME`:
    * The query parameter used to determine the language requested by a user during a HTTP request.
    * default: `glang`
* `GARNETT_ALLOW_BLANK_FALLBACK_OVERRIDE`
    * If set to true, when allpying the current language middleware, this will check for an extra get URL parameter to override the fallback to return blank strings where a languge has no content. This is useful for APIs
    * default: False

Advanced Settings (you probably don't need to adjust these)
* `GARNETT_TRANSLATABLE_FIELDS_PROPERTY_NAME`:
    * Garnett adds a property to all models that returns a list of all TranslatableFields. By default, this is 'translatable_fields', but you can customise it here if you want.
    * default: `translatable_fields`
* `GARNETT_TRANSLATIONS_PROPERTY_NAME`:
    * Garnett adds a property to all models that returns a dictionary of all translations of all TranslatableFields. By default, this is 'translations', but you can customise it here if you want.
    * default: `translations`

# Using Garnett

If you did everything above correctly, garnett should for the most part "just work".

## Switching the active language

Garnett comes with a handy context manager that can be used to specify the current language. In any place where you want to manually control the current language, wrap your code in `set_field_language` and garnett will correctly store the language. This can be nested, or you can change the language for a context multiple times before saving.

```python
from garnett.context import set_field_language
greeting = Greeting(text="Hello", target="World")

with set_field_language("en"):
    greeting.text = "Hello"
with set_field_language("fr"):
    greeting.text = "Bonjour"

greeting.save()
```

## Using Garnett with `values_list`

This is one of the areas that garnett _doesn't_ work immediately, but there is a solution.

In the places you are using values lists, wrap any translated field in an L-expression and the values list will return correctly. For example:

```python
from garnett.expressions import L
Book.objects.values_list(L("title"))
```

## Using Garnett with Django-Rest-Framework

As `TranslationField`s are based on JSONField, by default Django-Rest-Framework renders these as a JSONField, which may not be ideal.

You can get around this by using the `TranslatableSerializerMixin` _as the first mixin_, which adds the necessary hooks to your serializer. This will mean class changes, but you won't need to update or override every field.

For example:

```
from rest_framework import serializers
from library_app import models
from garnett.ext.drf import TranslatableSerializerMixin


class BookSerializer(TranslatableSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = "__all__"
```

This will allow you to set the value for a translatable as either a string for the active langauge, or by setting a dictionary that has all languages to be saved (note: this will override the existing language set).
For example:

To override just the active language: 

    curl -X PATCH ... -d "{  \"title\": \"Hello\"}"

To specifically override a single language (for example, Klingon): 

    curl -X PATCH ...  -H  "X-Garnett-Language-Code: tlh" -d "{  \"title\": \"Hello\"}"

To override all languages:

    curl -X PATCH ... -d "{  \"title\": {\"en\": \"Hello\", \"fr\": \"Bonjour\"}}"

## Using Garnett with django-reversion and django-reversion-compare

There are a few minor tweaks required to get Garnett to operate properly with
django-reversion and django-reversion-compare based on how they serialise and display data.

This is because Garnett does not use the same 'field.attname' and 'field.name' which means serialization in Django will not work correctly.

To get django-reversion to work you will need to use a translation-aware serialiser and apply a patch to ensure that django-reversion-compare can show the right information.

An example json translation-aware serializer is included with Garnett and this can be applied with the following two settings in `settings.py`:

```
# In settings.py

GARNETT_PATCH_REVERSION_COMPARE = True
SERIALIZATION_MODULES = {"json": "garnett.serializers.json"}
```

TranslatedFields will list the history and changes in json, but it does do comparisons correctly.

## Why call it Garnett?

* Libraries need a good name.
* Searching for "Famous Translators" will tell you about [Constance Garnett](https://en.wikipedia.org/wiki/Constance_Garnett).
* Searching for "Django Garnett" showed there was no python library with this name.
* It did however talk about [Garnet Clark](https://en.wikipedia.org/wiki/Garnet_Clark) (also spelled Garnett), a jazz pianist who played with Django Reinhart - the namesake of the Django Web Framework.
* Voila - a nice name

## Warnings

* `contains` acts like `icontains` on SQLite only when doing a contains query
 it does a case insensitive search. I don't know why - https://www.youtube.com/watch?v=PgGNWRtceag
* Due to how django sets admin form fields you will not get the admin specific widgets like
  `AdminTextAreaWidget` on translated fields in the django admin site by default. They can however
  be specified explicitly on the corresponding admin model form.

## Want to help maintain this library?

There is a `/dev/` directory with a docker-compose stack you can ues to bring up a database and clean development environment.

## Want other options?

There are a few good options for adding translatable strings to Django that may meet other use cases. We've included a few other options here, their strengths and why we didn't go with them.

* [django-modeltranslation](https://github.com/deschler/django-modeltranslation)
  
   **Pros:** this library lets you apply translations to external apps, without altering their models.
   
   **Cons:** each translation adds an extra column, which means languages are specified in code, and can't be altered by users later.
* [django-translated-fields](https://github.com/matthiask/django-translated-fields)
  
   **Pros:** uses a great context processor for switching lanugages (which is where we got the idea for ours).
   
   **Cons:** Languages are specified in django-settings, and can't be altered by users later.
* [django-parler](https://github.com/django-parler/django-parler)
  
   **Pros:** Django admin site support.
   
   **Cons:** Languages are stored in a separate table and can't be altered by users later. Translated fields are specified in model meta, away from the fields definition which makes complex lookups harder.



[term-language-code]: https://docs.djangoproject.com/en/3.1/topics/i18n/#term-language-code
[django-how]: https://docs.djangoproject.com/en/3.1/topics/i18n/translation/#how-django-discovers-language-preference
[dunder-html]: https://code.djangoproject.com/ticket/7261