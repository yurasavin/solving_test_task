import factory

from sample.plans.models import Plan


class PlanFactory(factory.DjangoModelFactory):

    class Meta:
        model = Plan

    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    data_available = factory.Faker('pyint')
