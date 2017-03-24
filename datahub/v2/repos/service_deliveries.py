import datetime
import uuid

from datahub.interaction.models import ServiceDelivery
from datahub.v2.schemas.service_deliveries import ServiceDeliverySchema

DEFAULT = object()

_mapping = {
    ('company', 'Company'),
    ('contact', 'Contact'),
    ('country', 'Country'),
    ('dit_advisor', 'Advisor'),
    ('dit_team', 'Team'),
    ('sector', 'Sector'),
    ('service', 'Service'),
    ('status', 'Status'),
    ('uk_region', 'UKRegion')
}


mapping_attr_to_type = dict(_mapping)
mapping_type_to_attr = dict((v, k) for (k, v) in _mapping)


class ServiceDeliveryDatabaseRepo:
    """DB repo."""

    def __init__(self, config=None):
        """Initialise the repo using the config."""
        self.model = ServiceDelivery
        self.schema = ServiceDeliverySchema

    def get(self, object_id):
        """Get and return a single object by its id."""
        model_instance = self.model.objects.get(id=object_id)
        return model_to_json_api(model_instance, schema_instance=self.schema())

    def filter(self, company_id=DEFAULT, contact_id=DEFAULT, offset=0, limit=100):
        """Filter objects."""
        filters = {}
        if company_id != DEFAULT:
            filters['company__pk'] = company_id
        if contact_id != DEFAULT:
            filters['contact__pk'] = contact_id
        start, end = offset, offset + limit
        items = list(self.model.objects.filter(**filters).all()[start:end])
        return [model_to_json_api(item, self.schema()) for item in items]

    def upsert(self, data):
        """Insert or update an object."""
        return json_api_to_model(data, self.model)


def build_relationship(model_instance, attribute):
    """Build relationships object from models."""
    entity_name = mapping_attr_to_type[attribute]
    data_dict = {'data': {'type': entity_name, 'id': str(model_instance.pk)}}
    return data_dict


def build_attribute(model_instance, attribute):
    """Build attributes object from model."""
    value = getattr(model_instance, attribute, None)
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    else:
        return value


def model_to_json_api(model_instance, schema_instance):
    """Convert the model instance to the JSON api format."""
    attributes = dict()
    relationships = dict()
    for item in schema_instance:
        if item.name == 'attributes':
            for subitem in item:
                attributes[subitem.name] = build_attribute(model_instance, subitem.name)
        if item.name == 'relationships':
            for subitem in item:
                relationship_instance = getattr(model_instance, subitem.name, None)
                if relationship_instance:
                    relationships[subitem.name] = build_relationship(relationship_instance, subitem.name)
    return {
        'type': model_instance.ENTITY_NAME,
        'attributes': attributes,
        'relationships': relationships
    }


def json_api_to_model(data, model_class):
    """Take JSON api format data and tries to save or update a model instance."""
    model_attrs = data.get('attributes', {})
    for key, value in data.get('relationships', {}).items():
        model_attrs[key + '_id'] = value['data']['id']
    model_id = model_attrs.pop('id', None)
    if model_id:
        return update_model(model_class, model_attrs, model_id)
    else:
        return model_class.objects.create(**model_attrs)


def update_model(model_class, model_attrs, object_id):
    """Update an existing model."""
    obj = model_class.objects.get(pk=object_id)
    for key, value in model_attrs.items():
        setattr(obj, key, value)
    obj.save()
    return obj
