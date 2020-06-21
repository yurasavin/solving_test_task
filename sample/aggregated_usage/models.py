from django.db import models

from sample.att_subscriptions.models import ATTSubscription
from sample.sprint_subscriptions.models import SprintSubscription


class AbstractAggregatedModel(models.Model):
    """Abstract model for aggregate usage data"""
    price = models.DecimalField(decimal_places=4, max_digits=9, default=0)
    usage_date = models.DateField()

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

    class Meta:
        abstract = True


class AggregatedDataUsage(AbstractAggregatedModel):
    """Raw data usage record for a subscription"""
    kilobytes_used = models.IntegerField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['usage_date', 'att_subscription'],
                name='unique_data_att_and_date',
            ),
            models.UniqueConstraint(
                fields=['usage_date', 'sprint_subscription'],
                name='unique_data_sprint_and_date',
            ),
        ]


class AggregatedVoiceUsage(AbstractAggregatedModel):
    """Raw voice usage record for a subscription"""
    seconds_used = models.IntegerField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['usage_date', 'att_subscription'],
                name='unique_voice_att_and_date',
            ),
            models.UniqueConstraint(
                fields=['usage_date', 'sprint_subscription'],
                name='unique_voice_sprint_and_date',
            ),
        ]
