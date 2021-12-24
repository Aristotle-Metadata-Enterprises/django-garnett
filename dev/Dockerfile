FROM python:3.8-buster

# Install python package management tools
RUN pip install --upgrade setuptools pip poetry tox

COPY ./* /usr/src/app/
WORKDIR /usr/src/app

RUN poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --no-root

ENV PYTHONPATH=/usr/src/app

