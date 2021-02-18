from django.apps.registry import Apps
from django.db.migrations import RunPython
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from garnett.utils import get_current_language
import json
from typing import Dict, List


def get_migration(app_label: str, model_fields: Dict[str, List[str]]) -> RunPython:
    """Generate a migration operation to prepare text fields for being translated

    Args:
        app_label: label for django app the migration is in
        model_fields: mapping of model name to list of text fields to migrate

    Returns:
        RunPython migration operation
    """

    def migrate_forwards(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
        current_lang = get_current_language()

        for model_name, fields in model_fields.items():
            updated = []
            model = apps.get_model(app_label, model_name)
            for item in model.objects.all():
                for field_name in fields:
                    value = getattr(item, field_name)
                    setattr(item, field_name, json.dumps({current_lang: value}))
                updated.append(item)

            model.objects.bulk_update(updated, fields)

    return RunPython(migrate_forwards)
