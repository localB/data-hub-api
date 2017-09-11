import datetime
import uuid
import factory

from django.utils.timezone import now

from datahub.company.test.factories import AdviserFactory, CompanyFactory, ContactFactory
from datahub.core.constants import Country, Sector
from datahub.core.test.factories import to_many_field

from datahub.omis.quote.test.factories import CancelledQuoteFactory, QuoteFactory

from ..constants import OrderStatus
from ..models import ServiceType


class OrderFactory(factory.django.DjangoModelFactory):
    """Order factory."""

    id = factory.LazyFunction(uuid.uuid4)
    created_by = factory.SubFactory(AdviserFactory)
    modified_by = factory.SubFactory(AdviserFactory)
    company = factory.SubFactory(CompanyFactory)
    contact = factory.LazyAttribute(lambda o: ContactFactory(company=o.company))
    primary_market_id = Country.france.value.id
    sector_id = Sector.aerospace_assembly_aircraft.value.id
    description = factory.Faker('text')
    contacts_not_to_approach = factory.Faker('text')
    product_info = factory.Faker('text')
    further_info = factory.Faker('text')
    existing_agents = factory.Faker('text')
    permission_to_approach_contacts = factory.Faker('text')
    delivery_date = factory.LazyFunction(
        lambda: (now() + datetime.timedelta(days=60)).date()
    )
    contact_email = factory.Faker('email')
    contact_phone = '+44 (0)7123 123456'
    status = OrderStatus.draft
    po_number = factory.Faker('text', max_nb_chars=50)

    @to_many_field
    def service_types(self):
        """
        Add support for setting service_types.
        If nothing specified when instantiating the object, the value returned by
        this method will be used by default.
        """
        return ServiceType.objects.filter(disabled_on__isnull=True).order_by('?')[:2]

    class Meta:  # noqa: D101
        model = 'order.Order'


class OrderWithOpenQuoteFactory(OrderFactory):
    """Order factory with an active quote."""

    quote = factory.SubFactory(QuoteFactory)
    status = OrderStatus.quote_awaiting_acceptance


class OrderWithCancelledQuoteFactory(OrderFactory):
    """Order factory with a cancelled quote."""

    quote = factory.SubFactory(CancelledQuoteFactory)


class OrderSubscriberFactory(factory.django.DjangoModelFactory):
    """Order Subscriber factory."""

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    adviser = factory.SubFactory(AdviserFactory)

    class Meta:  # noqa: D101
        model = 'order.OrderSubscriber'


class OrderAssigneeFactory(factory.django.DjangoModelFactory):
    """Order Assignee factory."""

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    adviser = factory.SubFactory(AdviserFactory)
    estimated_time = 120

    class Meta:  # noqa: D101
        model = 'order.OrderAssignee'
