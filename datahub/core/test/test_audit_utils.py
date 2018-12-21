import unittest.mock
import uuid

import pytest
from django.db import models

from datahub.company.models import Advisor
from datahub.company.test.factories import AdviserFactory
from datahub.core.audit_utils import (
    _get_changes,
    _get_db_field_from_column_name,
    _get_friendly_repr_of_object_reference,
    _get_value_for_field,
    diff_revisions,
    is_not_empty_or_none,
)
from datahub.investment.models import InvestmentProject


pytestmark = pytest.mark.django_db


def test_audit_diff_revisions():
    """Test audit diff revisions."""
    given = {
        'old': {
            'email': 'val1',
            'first_name': 'val2',
            'contact_email': 'contact',
            'old_email': 'hello',
            'telephone_number': None,
        },
        'new': {
            'email': 'val1',
            'first_name': 'new-val',
            'last_name': 'added',
            'telephone_number': '',
        },
    }

    expected = {
        'first_name': ['val2', 'new-val'],
        'last_name': [None, 'added'],
    }

    result = diff_revisions(Advisor._meta, given['old'], given['new'])
    assert result == expected


@pytest.mark.parametrize(
    'value,expected_result',
    (
        (None, False),
        ('', False),
        (False, True),
        ([], True),
        ('hello', True),
    ),
)
def test_is_not_empty_or_none(value, expected_result):
    """Tests if value is not empty or none."""
    assert is_not_empty_or_none(value) == expected_result


@pytest.mark.parametrize(
    'old_version,new_version,expected_result',
    (
        ({}, {}, {}),
        ({}, {'hello': 1}, {'hello': [None, 1]}),
        ({'hello': 1}, {}, {}),
        ({'hello': None}, {'hello': ''}, {'hello': [None, '']}),
    ),
)
def test_get_changes(old_version, new_version, expected_result):
    """Tests get changes between two dictionaries"""
    assert _get_changes(old_version, new_version) == expected_result


@pytest.mark.parametrize(
    'column_name,expected_type',
    (
        ('hello', type(None)),
        ('last_name', models.CharField),
        ('dit_team', models.ForeignKey),
    ),
)
def test_get_db_field_from_column_name(column_name, expected_type):
    """Test getting the db field for a given column name."""
    result = _get_db_field_from_column_name(Advisor._meta, column_name)
    assert type(result) is expected_type


def test_get_friendly_repr_of_object_reference_for_existing_object():
    """Test getting representation of existing object."""
    advisor = AdviserFactory()
    assert _get_friendly_repr_of_object_reference(Advisor, advisor.pk) == str(advisor)


@pytest.mark.parametrize(
    'value',
    (
        ('hello',),
        (str(uuid.uuid4()),),
        (1,),
    ),
)
def test_get_friendly_repr_of_object_reference_returns_value_when_no_object_found(value):
    """Test getting representation for an object that no longer exists."""
    assert _get_friendly_repr_of_object_reference(Advisor, value) == value


@pytest.mark.parametrize(
    'field_name,values,expected_result,number_of_times_get_repr_called',
    (
        ('investor_company', 'value', 'fake', 1),
        ('description', 'value', 'value', 0),
        ('client_contacts', ['value1', 'value2'], ['fake', 'fake'], 2),
    ),
)
@unittest.mock.patch('datahub.core.audit_utils._get_friendly_repr_of_object_reference')
def test_get_value_for_field_(
    mock_get_repr, field_name, values, expected_result, number_of_times_get_repr_called,
):
    """
    Test get value for a given field.
    Tests foreign key, many to many and char fields.
    """
    mock_get_repr.return_value = 'fake'
    field = _get_db_field_from_column_name(InvestmentProject._meta, field_name)
    result = _get_value_for_field(field, values)
    assert mock_get_repr.call_count == number_of_times_get_repr_called
    assert result == expected_result
