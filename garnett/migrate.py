from django.apps.registry import Apps
from django.db.migrations import RunPython
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from garnett.utils import get_current_language_code
import json
from typing import Callable, Dict, List


def _get_migrate_function(
    app_label: str,
    model_fields: Dict[str, List[str]],
    update: Callable[[str, str], str],
) -> Callable[[Apps, BaseDatabaseSchemaEditor], None]:
    """Generate a migration function given an update function for each value

    update is a function taking current language and old value and returning a new value
    """

    def migrate(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
        current_lang = get_current_language_code()

        for model_name, fields in model_fields.items():
            updated = []
            model = apps.get_model(app_label, model_name)
            for item in model.objects.all():
                for field_name in fields:
                    # Set new value retrieved from update function
                    value = getattr(item, field_name)
                    setattr(item, field_name, update(current_lang, value))
                updated.append(item)

            # Bulk update only the required fields
            model.objects.bulk_update(updated, fields)

    return migrate


def get_migration(app_label: str, model_fields: Dict[str, List[str]]) -> RunPython:
    """Generate a migration operation to prepare text fields for being translated

    Args:
        app_label: label for django app the migration is in
        model_fields: mapping of model name to list of text fields to migrate

    Returns:
        RunPython migration operation
    """

    def update_forwards(current_lang: str, value: str) -> str:
        return json.dumps({current_lang: value})

    def update_backwards(current_lang: str, value: str) -> str:
        return json.loads(value)[current_lang]

    return RunPython(
        code=_get_migrate_function(app_label, model_fields, update_forwards),
        reverse_code=_get_migrate_function(app_label, model_fields, update_backwards),
    )
