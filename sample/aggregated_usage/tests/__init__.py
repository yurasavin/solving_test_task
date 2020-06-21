import factory

from sample.aggregated_usage.models import (AggregatedDataUsage,
                                            AggregatedVoiceUsage)


class AggregatedDataUsageFactory(factory.DjangoModelFactory):

    class Meta:
        model = AggregatedDataUsage
        django_get_or_create = (
            'usage_date',
            'att_subscription',
            'sprint_subscription',
        )

    price = factory.Faker('pydecimal', left_digits=2, right_digits=4, positive=True)
    usage_date = factory.Faker('date_between', start_date='-1y', end_date='now')
    kilobytes_used = factory.Faker('pyint')
    att_subscription = None
    sprint_subscription = None


class AggregatedVoiceUsageFactory(factory.DjangoModelFactory):

    class Meta:
        model = AggregatedVoiceUsage
        django_get_or_create = (
            'usage_date',
            'att_subscription',
            'sprint_subscription',
        )

    price = factory.Faker('pydecimal', left_digits=2, right_digits=4, positive=True)
    usage_date = factory.Faker('date_between', start_date='-1y', end_date='now')
    seconds_used = factory.Faker('pyint')
    att_subscription = None
    sprint_subscription = None
