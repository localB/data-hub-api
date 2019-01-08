import unittest.mock

import pytest

from datahub.core.audit_utils import (
    _are_values_different,
    _get_changes,
    _get_field_or_none,
    _get_object_name_for_pk,
    _get_value_for_field,
    diff_versions,
)
from datahub.core.test.support.models import Book
from datahub.core.test.support.factories import BookFactory

pytestmark = pytest.mark.django_db


def test_audit_diff_versions():
    """Test audit diff versions."""
    given = {
        'old': {
            'date_published': 'val1',
            'name': 'val2',
            'contact_email': 'contact',
            'old_email': 'hello',
            'telephone_number': None,
            'old_field': '1',
        },
        'new': {
            'date_published': 'val1',
            'name': 'new-val',
            'genre': 'added',
            'telephone_number': '',
            'old_field': '2',
        },
    }

    expected = {
        'name': ['val2', 'new-val'],
        'genre': [None, 'added'],
        'old_field': ['1', '2'],
    }

    result = diff_versions(Book._meta, given['old'], given['new'])
    assert result == expected


@pytest.mark.parametrize(
    'old_value,new_value,expected_result',
    (
        ('', None, False),
        ('', False, True),
        ('hello', 'hello', False),
        (None, None, False),
        ('', '', False),
    ),
)
def test_are_values_different(old_value, new_value, expected_result):
    """Tests two values are different but that a blank string is treated as a None."""
    assert _are_values_different(old_value, new_value) == expected_result


@pytest.mark.parametrize(
    'old_version,new_version,expected_result',
    (
        ({}, {}, {}),
        ({}, {'hello': 1}, {'hello': [None, 1]}),
        ({'hello': 1}, {}, {}),
        ({'hello': None}, {'hello': ''}, {}),
    ),
)
def test_get_changes(old_version, new_version, expected_result):
    """Tests get changes between two dictionaries"""
    assert _get_changes(old_version, new_version) == expected_result


@pytest.mark.parametrize(
    'field_name,values,expected_result,number_of_times_get_repr_called',
    (
        ('proofreader', 'value', 'fake', 1),
        ('name', 'value', 'value', 0),
        ('authors', ['value1', 'value2'], ['fake', 'fake'], 2),
    ),
)
@unittest.mock.patch('datahub.core.audit_utils._get_object_name_for_pk')
def test_get_value_for_field(
    mock_get_repr, field_name, values, expected_result, number_of_times_get_repr_called,
):
    """
    Test get value for a given field.
    Tests foreign key, many to many and char fields.
    """
    mock_get_repr.return_value = 'fake'
    field = _get_field_or_none(Book._meta, field_name)
    result = _get_value_for_field(field, values)
    assert mock_get_repr.call_count == number_of_times_get_repr_called
    assert result == expected_result


class TestGetFriendlyReprOfObjectReference:
    """Tests for get friendly repr of object reference"""

    def test_get_repr_for_existing_object(self):
        """Test getting representation of existing object."""
        book = BookFactory()
        assert _get_object_name_for_pk(Book, book.pk) == str(book)

    @pytest.mark.parametrize(
        'value',
        (
            'hello',
            'c33f4ce3-051a-11e9-aa56-c82a140516f8',
            1,
            [],
        ),
    )
    def test_get_repr_when_no_object_found_returns_value(self, value):
        """Test getting representation for an object that no longer exists."""
        assert _get_object_name_for_pk(Book, value) == value
