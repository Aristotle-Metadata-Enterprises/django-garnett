# django-garnett

need to run tests like this for now: PYTHONPATH=../ ./manage.py shell

# Why write a new Django field translator?

A few reasons:
* Most existing django field translation libraries are static, and add separate database columns per translation.
* We needed a library that could be added in without requiring a rewrite of a large code base.


## Why call it Garnett?

* Libraries need a good name.
* Searching for "Famous Translators" will tell you about [Constnace Garnett](https://en.wikipedia.org/wiki/Constance_Garnett), a famous translator.
* Searching for "Garnett Django" shows [Garnet Clark](https://en.wikipedia.org/wiki/Garnet_Clark), a jazz pianist who played with Django Reinhart - the namesake of the Django Web Framework.
