* Start the dev environment (including Postgres & MariaDB databases) with:

    ```
    docker-compose up
    ```

* After you have started the dev stack, start the tests with:

    ```
    docker-compose exec dev tox
    ```

* Relock with 

    ```
    docker-compose run dev poetry relock
    ```

* Testing using script and tox (so you don't have to remember the db urls):


    -e is the tox environment to run - eg. dj-31, dj-32 or dj-40
    -PSM are optional flags to run for Postgres, SQLite, MariaDB
    ```
    ./dev/local-test.sh -e dj-31 -PSM
    ```

* Reformat the file using black command:

    Run `black .` at the root directory of the project

* Testing against a specific database:

    DATABASE_URL=postgres://postgres:changeme@postgres_db/postgres tox -e dj-51