# Want to help maintain this library?

There is a `/dev/` directory with a docker-compose stack you can use to bring up a database and clean development environment.

## Running tests

Django Garnett is tested using a docker-compose environment so tests can be easily run locally against MariaDB, Postgres and SQLite.

To run tests:
*  ``cd ./dev`` 
* Start the docker environment - ``docker-compose up``
* Start a development shell - ``docker-compose exec dev bash``
* Run tests - ``tox``

## Code formating

This library uses [python-black][python-black] for formating, you can format your code so it passes linting by:
*  ``cd ./dev`` 
* Start the docker environment - ``docker-compose up``
* Start a development shell - ``docker-compose exec dev bash``
* Run tests - ``black .``

Then review and recommit your code and its ready to go.

[python-black]: https://github.com/psf/black