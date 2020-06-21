from django.contrib.auth import get_user_model

import factory

from sample.purchases.models import Purchase


# Обычно в проектах есть кастомная модель юзера и эта фабрика располагается там
class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user_{n}')


class PurchaseFactory(factory.DjangoModelFactory):

    class Meta:
        model = Purchase

    user = factory.SubFactory(UserFactory)
    amount = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    payment_date = factory.Faker('date_time_between', start_date='-30m', end_date='now')
