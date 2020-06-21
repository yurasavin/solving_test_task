import factory

from sample.att_subscriptions.models import ATTSubscription
from sample.plans.tests import PlanFactory
from sample.purchases.tests import UserFactory


class ATTSubscriptionFactory(factory.DjangoModelFactory):

    class Meta:
        model = ATTSubscription

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    device_id = factory.Faker('pystr', min_chars=10, max_chars=20)
    phone_number = factory.Faker('msisdn')
    phone_model = factory.Faker('word')
    network_type = factory.Faker('text', max_nb_chars=5)
