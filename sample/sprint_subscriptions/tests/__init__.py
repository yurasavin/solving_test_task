import factory

from sample.sprint_subscriptions.models import SprintSubscription
from sample.plans.tests import PlanFactory
from sample.purchases.tests import UserFactory


class SprintSubscriptionFactory(factory.DjangoModelFactory):

    class Meta:
        model = SprintSubscription

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    device_id = factory.Faker('pystr', min_chars=10, max_chars=20)
    phone_number = factory.Faker('msisdn')
    phone_model = factory.Faker('word')
    sprint_id = factory.Faker('pystr', min_chars=16, max_chars=16)
