from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ("library_app", "0001_initial"),
    ]

    operations = [TrigramExtension()]
