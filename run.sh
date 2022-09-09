#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/app:/app/tests/:/usr/src/app:/usr/src/app/tests/
export DJANGO_SETTINGS_MODULE=library_app.settings

django-admin migrate

python ./tests/library_app/utils.py

django-admin runserver 0.0.0.0:$PORT