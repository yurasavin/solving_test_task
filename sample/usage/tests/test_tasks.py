from datetime import date, timedelta
from random import randint

from faker import Faker

import pytest

from sample.aggregated_usage.models import (AggregatedDataUsage,
                                            AggregatedVoiceUsage)
from sample.att_subscriptions.tests import ATTSubscriptionFactory
from sample.sprint_subscriptions.tests import SprintSubscriptionFactory
from sample.usage.models import DataUsageRecord, VoiceUsageRecord
from sample.usage.tasks import aggregate_usages
from sample.usage.tests import DataUsageRecordFactory, VoiceUsageRecordFactory

faker = Faker()


@pytest.mark.django_db
def test_aggregate_usages_task():
    att_sub1 = ATTSubscriptionFactory()
    att_sub2 = ATTSubscriptionFactory()
    sprint_sub1 = SprintSubscriptionFactory()

    today = date.today()
    previous_day = today - timedelta(days=5)

    data_usage1 = DataUsageRecordFactory.create_batch(randint(1, 15), att_subscription=att_sub1, usage_date=today)
    data_usage2 = DataUsageRecordFactory.create_batch(randint(1, 15), att_subscription=att_sub2, usage_date=today)
    data_usage3 = DataUsageRecordFactory.create_batch(randint(1, 15), sprint_subscription=sprint_sub1, usage_date=today)
    data_usage4 = DataUsageRecordFactory.create_batch(randint(1, 15), att_subscription=att_sub1, usage_date=previous_day)
    data_usage5 = DataUsageRecordFactory.create_batch(randint(1, 15), att_subscription=att_sub2, usage_date=previous_day)

    voice_usage1 = VoiceUsageRecordFactory.create_batch(randint(1, 15), att_subscription=att_sub1, usage_date=today)
    voice_usage2 = VoiceUsageRecordFactory.create_batch(randint(1, 15), sprint_subscription=sprint_sub1, usage_date=today)

    aggregate_usages(att_subscription_id=att_sub1.id, sprint_subscription_id=None, date=today, usage_type='data')
    aggregate_usages(att_subscription_id=att_sub2.id, sprint_subscription_id=None, date=today, usage_type='data')
    aggregate_usages(att_subscription_id=None, sprint_subscription_id=sprint_sub1.id, date=today, usage_type='data')
    aggregate_usages(att_subscription_id=att_sub1.id, sprint_subscription_id=None, date=previous_day, usage_type='data')
    aggregate_usages(att_subscription_id=att_sub2.id, sprint_subscription_id=None, date=previous_day, usage_type='data')
    aggregate_usages(att_subscription_id=None, sprint_subscription_id=sprint_sub1.id, date=today, usage_type='voice')
    aggregate_usages(att_subscription_id=att_sub1.id, sprint_subscription_id=None, date=today, usage_type='voice')

    assert DataUsageRecord.objects.count() == 0
    assert VoiceUsageRecord.objects.count() == 0

    agg = AggregatedDataUsage.objects.get(att_subscription_id=att_sub1, usage_date=today)
    assert agg.price == sum((d.price for d in data_usage1))

    agg = AggregatedDataUsage.objects.get(att_subscription_id=att_sub2, usage_date=today)
    assert agg.price == sum((d.price for d in data_usage2))

    agg = AggregatedDataUsage.objects.get(sprint_subscription_id=sprint_sub1, usage_date=today)
    assert agg.price == sum((d.price for d in data_usage3))

    agg = AggregatedDataUsage.objects.get(att_subscription_id=att_sub1, usage_date=previous_day)
    assert agg.price == sum((d.price for d in data_usage4))

    agg = AggregatedDataUsage.objects.get(att_subscription_id=att_sub2, usage_date=previous_day)
    assert agg.price == sum((d.price for d in data_usage5))

    agg = AggregatedVoiceUsage.objects.get(att_subscription_id=att_sub1, usage_date=today)
    assert agg.price == sum((d.price for d in voice_usage1))

    agg = AggregatedVoiceUsage.objects.get(sprint_subscription=sprint_sub1, usage_date=today)
    assert agg.price == sum((d.price for d in voice_usage2))

    # Add usage data same as data_usage1
    data_usage6 = DataUsageRecordFactory.create_batch(randint(1, 15), att_subscription=att_sub1, usage_date=today)
    aggregate_usages(att_subscription_id=att_sub1.id, sprint_subscription_id=None, date=today, usage_type='data')
    assert DataUsageRecord.objects.count() == 0
    agg = AggregatedDataUsage.objects.get(att_subscription_id=att_sub1, usage_date=today)
    assert agg.price == sum((d.price for d in data_usage1)) + sum((d.price for d in data_usage6))
