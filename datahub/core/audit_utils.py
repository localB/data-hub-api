from django.core.exceptions import ValidationError
from django.db import models


def diff_versions(model_meta_data, old_revision, new_revision):
    """Audit versions comparision with the delta returned."""
    changes = {}
    raw_changes = _get_changes(old_revision, new_revision)

    for db_field_name, values in raw_changes.items():
        field = _get_db_field_from_column_name(model_meta_data, db_field_name)
        if field and list(filter(is_not_empty_or_none, values)):
            changes[field.name] = [_get_value_for_field(field, value) for value in values]
    return changes


def is_not_empty_or_none(value):
    """Checks if value is not empty or none."""
    if value in ['', None]:
        return False
    return True


def _get_changes(old_version, new_version):
    """Compares dictionaries returning the delta between them."""
    changes = {}

    for field_name, new_value in new_version.items():
        if field_name not in old_version:
            changes[field_name] = [None, new_value]
        else:
            old_value = old_version[field_name]
            if old_value != new_value:
                changes[field_name] = [old_value, new_value]
    return changes


def _get_db_field_from_column_name(model_meta_data, db_field_name):
    """Gets django db field for a given column name"""
    try:
        return model_meta_data.get_field(db_field_name)
    except models.FieldDoesNotExist:
        return None


def _get_value_for_field(field, value):
    """Checks field type and if required retrieves friendly value from related model."""
    if type(field) is models.ForeignKey:
        return _get_friendly_repr_of_object_reference(field.related_model, value)
    if type(field) is models.ManyToManyField:
        return [
            _get_friendly_repr_of_object_reference(
                field.related_model, one_value,
            ) for one_value in value
        ]
    return value


def _get_friendly_repr_of_object_reference(db_model, value):
    """Gets friendly representation for a given object reference."""
    try:
        result = db_model.objects.get(pk=value)
    except ValidationError:
        return value
    except db_model.DoesNotExist:
        return value
    else:
        return str(result)
