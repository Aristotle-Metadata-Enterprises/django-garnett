FROM python:3.7

# Install python package management tools
RUN pip install --upgrade setuptools pip poetry

COPY ./* /usr/src/app/
WORKDIR /usr/src/app

RUN poetry lock && poetry install

ENV PYTHONPATH=/usr/src/app/garnett DJANGO_SETTINGS_MODULE=tests.settings
