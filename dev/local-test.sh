#!/bin/bash
# A little script to run on the different dev databases
RUN_PG=0
RUN_SQLITE=0
RUN_MARIA=0

while getopts e:PSM flag
do
    case "${flag}" in
        e) TOX_ENV=${OPTARG};;
        P) RUN_PG=1;;
        S) RUN_SQLITE=1;;
        M) RUN_MARIA=1;;
    esac
done

if [ $RUN_SQLITE -eq 1 ]
then
    echo "Testing with SQLLite"
    tox -e ${TOX_ENV} # Sqlite
fi

if [ $RUN_MARIA -eq 1 ]
then
    echo "Testing with MariaDB"
    DATABASE_URL=mysql://root:@maria_db:13306/test tox -e ${TOX_ENV}
fi

if [ $RUN_PG -eq 1 ]
then
    echo "Testing with Postgres"
    DATABASE_URL=postgres://postgres:changeme@postgres_db:5432/test tox -e ${TOX_ENV} # Sqlite
fi

