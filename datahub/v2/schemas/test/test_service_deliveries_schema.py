"""Service deliveries schema tests."""

import datetime
import unittest
import uuid

import colander
import pytest

from datahub.v2.schemas.service_deliveries import RelationshipType, ServiceDeliverySchema


class TestRelationshipType(unittest.TestCase):
    """Relationship type."""

    def setUp(self):
        """Create a dummy schema."""
        class MySchema(colander.MappingSchema):
            item = colander.SchemaNode(RelationshipType('flibble'))
        self.schema = MySchema

    def test_deserialize_empty(self):
        """Deserialize empty."""
        with pytest.raises(colander.Invalid) as e:
            self.schema().deserialize({'item': {}})
        assert e.value.asdict()['item'] == '{} has no key data'  # noqa: P103

    def test_deserialize_missing_type(self):
        """Deserialize missing type."""
        with pytest.raises(colander.Invalid) as e:
            self.schema().deserialize({'item': {'data': {}}})
        assert e.value.asdict()['item'] == """{'data': {}} has no key type"""

    def test_deserialize_incorrect_type(self):
        """Deserialize incorrect type."""
        with pytest.raises(colander.Invalid) as e:
            self.schema().deserialize({'item': {'data': {'type': 'bamble'}}})
        assert e.value.asdict()['item'] == 'type bamble should be flibble'

    def test_serialize_empty(self):
        """Serialize empty."""
        with pytest.raises(colander.Invalid) as e:
            self.schema().serialize({'item': {}})
        assert e.value.asdict()['item'] == '{} has no key data'  # noqa: P103

    def test_serialize_missing_type(self):
        """Serialize missing type."""
        with pytest.raises(colander.Invalid) as e:
            self.schema().serialize({'item': {'data': {}}})
        assert e.value.asdict()['item'] == """{'data': {}} has no key type"""

    def test_serialize_incorrect_type(self):
        """Serialize incorrect type."""
        with pytest.raises(colander.Invalid) as e:
            self.schema().serialize({'item': {'data': {'type': 'bamble'}}})
        assert e.value.asdict()['item'] == 'type bamble should be flibble'


def test_service_deliveries_schema_invalid():
    """SD schema test."""
    data = {
        'type': 'ServiceDeliver',
        'attributes': {
            'subject': 'whatever',
            'date': datetime.datetime.now().isoformat(),
            'notes': 'hello',
            'feedback': 'foo',
            'id': 'hello'
        },
        'relationships': {
            'status': {
                'data': {
                    'type': 'Status',
                    'id': 'constants.ServiceDeliveryStatus.offered.value.id'
                }
            },
            'company': {
                'data': {
                    'type': 'Company',
                    'id': 'CompanyFactory().pk'
                }
            },
            'contact': {
                'data': {
                    'type': 'Contact',
                    'id': 'ContactFactory().pk'
                }
            },
            'service': {
                'data': {
                    'type': 'Service',
                    'id': 'service_offer.service.id'
                }
            },
            'dit_team': {
                'data': {
                    'type': 'Team',
                    'id': 'service_offer.dit_team.id'
                }
            },
            'uk_region': {
                'data': {
                    'type': 'UKRegion',
                    'id': 'dsdasdsadsa'
                }
            },
            'sector': {
                'data': {
                    'type': 'Sector',
                    'id': 'dsdasdsadsa'
                }
            },
            'country_of_interest': {
                'data': {
                    'type': 'flibble',
                    'id': 'dsdasdsadsa'
                }
            },
            'event': {
                'data': {
                    'type': 'event',
                    'id': 'dsdasdsadsa'
                }
            },
        }
    }

    expected = {
        'attributes.id': 'Invalid UUID string',
        'type': 'Value must be ServiceDelivery',
        'relationships.country_of_interest': 'type flibble should be Country',
        'relationships.event': 'type event should be Event',
        'relationships.status': 'type ServiceDeliveryStatus should be ServiceDeliveryStatus'}

    with pytest.raises(colander.Invalid) as e:
        ServiceDeliverySchema().deserialize(data)

    assert e.value.asdict() == expected


def test_service_deliveries_valid_schema():
    """SD schema test."""
    data = {
        'type': 'ServiceDelivery',
        'attributes': {
            'subject': 'whatever',
            'date': datetime.datetime.now().isoformat(),
            'notes': 'hello',
            'id': str(uuid.uuid4())
        },
        'relationships': {
            'status': {
                'data': {
                    'type': 'ServiceDeliveryStatus',
                    'id': 'constants.ServiceDeliveryStatus.offered.value.id'
                }
            },
            'company': {
                'data': {
                    'type': 'Company',
                    'id': 'CompanyFactory().pk'
                }
            },
            'contact': {
                'data': {
                    'type': 'Contact',
                    'id': 'ContactFactory().pk'
                }
            },
            'service': {
                'data': {
                    'type': 'Service',
                    'id': 'service_offer.service.id'
                }
            },
            'dit_team': {
                'data': {
                    'type': 'Team',
                    'id': 'service_offer.dit_team.id'
                }
            },
        }
    }

    assert ServiceDeliverySchema().deserialize(data)
