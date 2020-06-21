import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker

import pytest

from sample.aggregated_usage.tests import (AggregatedDataUsageFactory,
                                           AggregatedVoiceUsageFactory)
from sample.att_subscriptions.models import ATTSubscription
from sample.att_subscriptions.tests import ATTSubscriptionFactory
from sample.sprint_subscriptions.models import SprintSubscription
from sample.sprint_subscriptions.tests import SprintSubscriptionFactory

faker = Faker()


@pytest.mark.django_db
class TestAggregatedUsageByPriceView:

    def test_aggregated_data_usage_by_price_serializer_view_list(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-price/?price=100')
        assert response.status_code == 200
        assert type(response.json()) == dict

    def test_aggregated_data_usage_by_price_serializer_view_float_param(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-price/?price=100.15')
        assert response.status_code == 200

    def test_aggregated_data_usage_by_price_serializer_view_whthout_param(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-price/')
        assert response.status_code == 400

    def test_aggregated_data_usage_by_price_serializer_view_empty_param(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-price/?price=')
        assert response.status_code == 400

    def test_aggregated_data_usage_by_price_serializer_view_alpha_param(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-price/?price=abc')
        assert response.status_code == 400

    def test_aggregated_data_usage_by_price_serializer_view_negative_param(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-price/?price=-100')
        assert response.status_code == 400

    def test_aggregated_data_usage_by_price_serializer_view_response(self, api_client):
        # Create some subscribes
        att_subscribes = ATTSubscriptionFactory.create_batch(10)
        sprint_subscribes = SprintSubscriptionFactory.create_batch(10)

        # Create some usage data
        [AggregatedDataUsageFactory.create_batch(faker.pyint(max_value=15), att_subscription=sub) for sub in att_subscribes]
        [AggregatedDataUsageFactory.create_batch(faker.pyint(max_value=15), sprint_subscription=sub) for sub in sprint_subscribes]

        # Create some usage voice
        [AggregatedVoiceUsageFactory.create_batch(faker.pyint(max_value=15), att_subscription=sub) for sub in att_subscribes]
        [AggregatedVoiceUsageFactory.create_batch(faker.pyint(max_value=15), sprint_subscription=sub) for sub in sprint_subscribes]

        for price in [0, 100, 777, 4126, 15000, 90000, 124.23, 8.2223]:
            response = api_client.get(f'/api/v1/aggregated-usage-by-price/?price={price}')
            assert response.status_code == 200
            response_data = response.json()

            decimal_price = Decimal(str(price))

            for subscribe_data in response_data['att_subscriptions']:
                subscribe = ATTSubscription.objects.get(id=subscribe_data['id'])
                total_data_prices = sum((a.price for a in subscribe.aggregateddatausage_set.all()))
                total_voice_prices = sum((a.price for a in subscribe.aggregatedvoiceusage_set.all()))

                data_excess = total_data_prices - decimal_price
                if data_excess <= 0:
                    assert subscribe_data['data_excess'] is None
                else:
                    assert data_excess == Decimal(subscribe_data['data_excess'])

                voice_excess = total_voice_prices - decimal_price
                if voice_excess <= 0:
                    assert subscribe_data['voice_excess'] is None
                else:
                    assert voice_excess == Decimal(subscribe_data['voice_excess'])

            for subscribe_data in response_data['sprint_subscriptions']:
                subscribe = SprintSubscription.objects.get(id=subscribe_data['id'])
                total_data_prices = sum((a.price for a in subscribe.aggregateddatausage_set.all()))
                total_voice_prices = sum((a.price for a in subscribe.aggregatedvoiceusage_set.all()))

                data_excess = total_data_prices - decimal_price
                if data_excess <= 0:
                    assert subscribe_data['data_excess'] is None
                else:
                    assert data_excess == Decimal(subscribe_data['data_excess'])

                voice_excess = total_voice_prices - decimal_price
                if voice_excess <= 0:
                    assert subscribe_data['voice_excess'] is None
                else:
                    assert voice_excess == Decimal(subscribe_data['voice_excess'])


@pytest.mark.django_db
class TestAggregatedUsageByDateView:

    def test_aggregated_data_usage_by_date_serializer_view_list(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date=2020-01-11&to_date=2020-01-11&usage_type=data')
        assert response.status_code == 200
        assert type(response.json()) == dict

        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date=2020-01-11&to_date=2020-01-11&usage_type=voice')
        assert response.status_code == 200
        assert type(response.json()) == dict

    def test_aggregated_data_usage_by_date_serializer_view_from_date_greater_then_to_date(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date=2020-05-11&to_date=2020-01-11&usage_type=data')
        assert response.status_code == 400

    def test_aggregated_data_usage_by_date_serializer_view_whthout_param(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?to_date=2020-01-11&usage_type=data')
        assert response.status_code == 400

        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date=2020-05-11&usage_type=data')
        assert response.status_code == 400

        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date=2020-05-11&to_date=2020-01-11')
        assert response.status_code == 400

    def test_aggregated_data_usage_by_date_serializer_view_wrong_usage_type_param(self, api_client):
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date=2020-01-11&to_date=2020-01-11&usage_type=abc')
        assert response.status_code == 400

    def test_aggregated_data_usage_by_date_serializer_view_response(self, api_client):
        # Create some subscribes
        att_subscribes = ATTSubscriptionFactory.create_batch(10)
        sprint_subscribes = SprintSubscriptionFactory.create_batch(10)

        # Create days for filtering
        today = date.today()
        previous_day = today - timedelta(days=5)
        null_day = today - timedelta(days=2)

        # Create some usage data
        [AggregatedDataUsageFactory(usage_date=today, att_subscription=sub) for
         sub in att_subscribes if random.choice([0, 1]) == 1]
        [AggregatedDataUsageFactory(usage_date=previous_day, att_subscription=sub) for
         sub in att_subscribes if random.choice([0, 1]) == 1]

        [AggregatedDataUsageFactory(usage_date=today, sprint_subscription=sub) for
         sub in sprint_subscribes if random.choice([0, 1]) == 1]
        [AggregatedDataUsageFactory(usage_date=previous_day, sprint_subscription=sub) for
         sub in sprint_subscribes if random.choice([0, 1]) == 1]

        # Create some usage voice
        [AggregatedVoiceUsageFactory(usage_date=today, att_subscription=sub) for
         sub in att_subscribes if random.choice([0, 1]) == 1]
        [AggregatedVoiceUsageFactory(usage_date=previous_day, att_subscription=sub) for
         sub in att_subscribes if random.choice([0, 1]) == 1]

        [AggregatedVoiceUsageFactory(usage_date=today, sprint_subscription=sub) for
         sub in sprint_subscribes if random.choice([0, 1]) == 1]
        [AggregatedVoiceUsageFactory(usage_date=previous_day, sprint_subscription=sub) for
         sub in sprint_subscribes if random.choice([0, 1]) == 1]

        # Test getting today data usage
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date={today}&to_date={today}&usage_type=data')
        assert response.status_code == 200
        response_data = response.json()

        for subscribe_data in response_data['att_subscriptions']:
            subscribe = ATTSubscription.objects.get(id=subscribe_data['id'])
            total_data_usage = sum((a.price for a in subscribe.aggregateddatausage_set.all()))
            date_data_usage = sum((a.price for a in subscribe.aggregateddatausage_set.all() if a.usage_date == today))

            assert total_data_usage == Decimal(subscribe_data['total_usage'])
            assert date_data_usage == Decimal(subscribe_data['date_usage'])

        for subscribe_data in response_data['sprint_subscriptions']:
            subscribe = SprintSubscription.objects.get(id=subscribe_data['id'])
            total_data_usage = sum((a.price for a in subscribe.aggregateddatausage_set.all()))
            date_data_usage = sum((a.price for a in subscribe.aggregateddatausage_set.all() if a.usage_date == today))

            assert total_data_usage == Decimal(subscribe_data['total_usage'])
            assert date_data_usage == Decimal(subscribe_data['date_usage'])

        # Test getting today voice usage
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date={today}&to_date={today}&usage_type=voice')
        assert response.status_code == 200
        response_data = response.json()

        for subscribe_data in response_data['att_subscriptions']:
            subscribe = ATTSubscription.objects.get(id=subscribe_data['id'])
            total_data_usage = sum((a.price for a in subscribe.aggregatedvoiceusage_set.all()))
            date_data_usage = sum((a.price for a in subscribe.aggregatedvoiceusage_set.all() if a.usage_date == today))

            assert total_data_usage == Decimal(subscribe_data['total_usage'])
            assert date_data_usage == Decimal(subscribe_data['date_usage'])

        for subscribe_data in response_data['sprint_subscriptions']:
            subscribe = SprintSubscription.objects.get(id=subscribe_data['id'])
            total_data_usage = sum((a.price for a in subscribe.aggregatedvoiceusage_set.all()))
            date_data_usage = sum((a.price for a in subscribe.aggregatedvoiceusage_set.all() if a.usage_date == today))

            assert total_data_usage == Decimal(subscribe_data['total_usage'])
            assert date_data_usage == Decimal(subscribe_data['date_usage'])

        # Test getting null day data usage
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date={null_day}&to_date={null_day}&usage_type=data')
        assert response.status_code == 200
        response_data = response.json()

        assert not response_data['att_subscriptions']
        assert not response_data['sprint_subscriptions']

        # Test getting date range data usage
        response = api_client.get(f'/api/v1/aggregated-usage-by-date/?from_date={previous_day}&to_date={today}&usage_type=data')
        assert response.status_code == 200
        response_data = response.json()

        for subscribe_data in response_data['att_subscriptions']:
            subscribe = ATTSubscription.objects.get(id=subscribe_data['id'])
            date_data_usage = total_data_usage = sum((a.price for a in subscribe.aggregateddatausage_set.all()))

            assert total_data_usage == Decimal(subscribe_data['total_usage'])
            assert date_data_usage == Decimal(subscribe_data['date_usage'])

        for subscribe_data in response_data['sprint_subscriptions']:
            subscribe = SprintSubscription.objects.get(id=subscribe_data['id'])
            date_data_usage = total_data_usage = sum((a.price for a in subscribe.aggregateddatausage_set.all()))

            assert total_data_usage == Decimal(subscribe_data['total_usage'])
            assert date_data_usage == Decimal(subscribe_data['date_usage'])
