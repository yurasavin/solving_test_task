from django.db import models

from sample.att_subscriptions.models import ATTSubscription
from sample.sprint_subscriptions.models import SprintSubscription


class AbstractUsageRecord(models.Model):
    """Abstract model for different types of raw usage for a subscription"""

    att_subscription = models.ForeignKey(
        ATTSubscription,
        null=True,
        on_delete=models.PROTECT,
    )
    sprint_subscription = models.ForeignKey(
        SprintSubscription,
        null=True,
        on_delete=models.PROTECT,
    )
    # Под price понимаем суммарную стоимость данных/секунд
    price = models.DecimalField(decimal_places=4, max_digits=7, default=0)
    usage_date = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class DataUsageRecord(AbstractUsageRecord):
    """Raw data usage record for a subscription"""

    kilobytes_used = models.IntegerField(null=False)


class VoiceUsageRecord(AbstractUsageRecord):
    """Raw voice usage record for a subscription"""

    seconds_used = models.IntegerField(null=False)
