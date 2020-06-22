from django.db import transaction
from django.db.models import Count, Sum

from celery import shared_task
from celery.utils.log import get_task_logger

from sample.aggregated_usage.models import (AggregatedDataUsage,
                                            AggregatedVoiceUsage)
from sample.usage.models import DataUsageRecord, VoiceUsageRecord

logger = get_task_logger(__name__)


@shared_task(name='run_aggregate_usages')
def run_aggregate_usages():
    """
    Group DataUsageRecord's and VoiceUsageRecord's by
    subscription and date, and run aggregate task
    """
    usage_datas = DataUsageRecord.objects\
        .values('att_subscription', 'sprint_subscription', 'usage_date__date')\
        .annotate(total_price=Count('price'))\
        .order_by('att_subscription')

    for usage_data in usage_datas.iterator():
        aggregate_usages.delay(
            att_subscription_id=usage_data['att_subscription'],
            sprint_subscription_id=usage_data['sprint_subscription'],
            date=usage_data['usage_date__date'],
            usage_type='data',
        )

    usage_voices = VoiceUsageRecord.objects\
        .values('att_subscription', 'sprint_subscription', 'usage_date__date')\
        .annotate(total_price=Count('price'))\
        .order_by('att_subscription')

    for usage_voice in usage_voices.iterator():
        aggregate_usages.delay(
            att_subscription_id=usage_data['att_subscription'],
            sprint_subscription_id=usage_data['sprint_subscription'],
            date=usage_data['usage_date__date'],
            usage_type='voice',
        )


@shared_task(name='aggregate_usages')
def aggregate_usages(
        att_subscription_id,
        sprint_subscription_id,
        date,
        usage_type):
    """
    Create or update AggregatedDataUsage for the passed parameters
    """
    if usage_type == 'data':
        model, agg_model, used_f = DataUsageRecord, AggregatedDataUsage, 'kilobytes_used'  # noqa: E501
    elif usage_type == 'voice':
        model, agg_model, used_f = VoiceUsageRecord, AggregatedVoiceUsage, 'seconds_used'  # noqa: E501

    usage_qs = model.objects.filter(
        att_subscription_id=att_subscription_id,
        sprint_subscription_id=sprint_subscription_id,
        usage_date__date=date,
    )
    usage_ids = list(usage_qs.values_list('id', flat=True))
    aggregated_qs = usage_qs.aggregate(
        total_price=Sum('price'),
        total_used=Sum(used_f),
    )

    with transaction.atomic():
        aggregated_data, _ = agg_model.objects.get_or_create(
            att_subscription_id=att_subscription_id,
            sprint_subscription_id=sprint_subscription_id,
            usage_date=date,
        )
        aggregated_data.price += aggregated_qs['total_price']
        old_used = getattr(aggregated_data, used_f)
        new_used = old_used + aggregated_qs['total_used']
        setattr(aggregated_data, used_f, new_used)
        aggregated_data.save(update_fields=['price', used_f])

        while usage_ids:
            chunk = usage_ids[:1000]
            usage_ids = usage_ids[1000:]
            model.objects.filter(id__in=chunk).delete()
