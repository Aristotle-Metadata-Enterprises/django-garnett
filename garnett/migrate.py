import base64
import json
import pickle
from django.apps.registry import Apps
from django.db.migrations import RunPython
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from garnett.utils import get_current_language_code
from typing import Callable, Dict, List


"""
These methods convert a string to and from a safe base64 encoded version of text.
This helps with database encoding
"""


def safe_encode(value: str) -> str:
    return base64.b64encode(pickle.dumps(value)).decode("ascii")


def safe_decode(value: str) -> str:
    return pickle.loads(base64.urlsafe_b64decode(value))


def _get_migrate_function(
    app_label: str,
    model_fields: Dict[str, List[str]],
    update: Callable[[str, str], str],
    ts_all: bool = False,
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
                    if ts_all:
                        field_name = f"{field_name}_tsall"
                    value = getattr(item, field_name)
                    setattr(item, field_name, update(current_lang, value))
                updated.append(item)

            # Bulk update only the required fields
            model.objects.bulk_update(updated, fields)

    return migrate


# Part 1


def update_safe_encode_content_forwards(current_lang: str, value: str) -> str:
    value = safe_encode(value)
    return json.dumps({current_lang: value})


def update_safe_encode_content_backwards(current_lang: str, value: str) -> str:
    value = json.loads(value)
    return safe_decode(value.get(current_lang, safe_encode("")))


def step_1_safe_encode_content(
    app_label: str, model_fields: Dict[str, List[str]]
) -> RunPython:
    """Generate a migration operation to safely store text content prior to field migration
    This is needed as standard json is not escaped according to Postgres (and maybe other database) requirements.
    For example, Postgres requires single quotes (') to be double escaped: ('')
    For more info see here: https://stackoverflow.com/questions/35677204/psql-insert-json-with-double-quotes-inside-strings

    Args:
        app_label: label for django app the migration is in
        model_fields: mapping of model name to list of text fields to migrate

    Returns:
        RunPython migration operation
    """

    return RunPython(
        code=_get_migrate_function(
            app_label, model_fields, update_safe_encode_content_forwards
        ),
        reverse_code=_get_migrate_function(
            app_label, model_fields, update_safe_encode_content_backwards, ts_all=True
        ),
    )


# Part 2


def update_safe_prepare_translations_forwards(current_lang: str, value: dict) -> dict:
    value = safe_decode(value.get(current_lang, safe_encode("")))
    return {current_lang: value}


def update_safe_prepare_translations_backwards(current_lang: str, value: dict) -> dict:
    value = safe_encode(value.get(current_lang, ""))
    return {current_lang: value}


def step_2_safe_prepare_translations(
    app_label: str, model_fields: Dict[str, List[str]]
) -> RunPython:
    """Generate a migration operation to prepare text fields for being translated

    Args:
        app_label: label for django app the migration is in
        model_fields: mapping of model name to list of text fields to migrate

    Returns:
        RunPython migration operation
    """

    return RunPython(
        code=_get_migrate_function(
            app_label,
            model_fields,
            update_safe_prepare_translations_forwards,
            ts_all=True,
        ),
        reverse_code=_get_migrate_function(
            app_label,
            model_fields,
            update_safe_prepare_translations_backwards,
            ts_all=True,
        ),
    )
