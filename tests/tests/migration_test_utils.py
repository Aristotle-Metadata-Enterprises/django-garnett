import unittest
from typing import List, Tuple, Union

from django.apps import apps as nowapps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


# This is an object so it is not run as a test itself. See usage in main.test_migrations
@unittest.skipIf(
    connection.vendor in ["microsoft", "mssql", "mariadb", "mysql"],
    "Migration tests are not supported by the current database",
)
class MigrationsTestCase(object):
    """
    Thanks to: https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    """

    @property
    def app(self):
        return nowapps.get_containing_app_config(type(self).__module__).name

    migrate_from: Union[str, List[Tuple]] = None
    migrate_to: Union[str, List[Tuple]] = None

    def setUp(self):
        assert (
            self.migrate_from and self.migrate_to
        ), "TestCase '{}' must define migrate_from and migrate_to properties".format(
            type(self).__name__
        )
        if type(self.migrate_from) is not list:
            self.migrate_from = [(self.app, self.migrate_from)]
        if type(self.migrate_to) is not list:
            self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        # print('unmigrated: %s'%executor.loader.unmigrated_apps)
        # print('migrated: %s'%executor.loader.migrated_apps)

        # executor.loader.build_graph()  # reload.
        old_apps = executor.loader.project_state(self.migrate_from).apps

        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass
