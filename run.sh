set PYTHONPATH=$PYTHONPATH:/app:/app/tests/:/usr/src/app:/usr/src/app/tests/

django-admin migrate

python ./tests/library_app/utils.py

django-admin runserver 0.0.0.0:$PORT