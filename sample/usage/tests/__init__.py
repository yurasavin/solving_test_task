import factory

from sample.purchases.tests import PurchaseFactory
from sample.usage.models import DataUsageRecord, VoiceUsageRecord


class DataUsageRecordFactory(factory.DjangoModelFactory):

    class Meta:
        model = DataUsageRecord

    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    usage_date = factory.Faker('date_time_between', start_date='-150d', end_date='now')
    kilobytes_used = factory.Faker('pyint')


class VoiceUsageRecordFactory(factory.DjangoModelFactory):

    class Meta:
        model = VoiceUsageRecord

    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    usage_date = factory.Faker('date_time_between', start_date='-150d', end_date='now')
    seconds_used = factory.Faker('pyint')
