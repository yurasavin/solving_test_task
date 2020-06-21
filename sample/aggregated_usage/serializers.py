from rest_framework import serializers

from sample.att_subscriptions.serializers import (
    ATTAggregateByDateSerializer, ATTAggregateByPriceSerializer)
from sample.sprint_subscriptions.serializers import (
    SprintAggregateByDateSerializer, SprintAggregateByPriceSerializer)


class PriceParamSerializer(serializers.Serializer):

    price = serializers.DecimalField(
        max_digits=20,
        decimal_places=4,
        min_value=0,
    )


class DateParamSerializer(serializers.Serializer):

    date = serializers.DateField()


class AggregatedUsageByPriceSerializer(serializers.Serializer):

    att_subscriptions = ATTAggregateByPriceSerializer(many=True)
    sprint_subscriptions = SprintAggregateByPriceSerializer(many=True)


class AggregatedUsageByDateSerializer(serializers.Serializer):

    att_subscriptions = ATTAggregateByDateSerializer(many=True)
    sprint_subscriptions = SprintAggregateByDateSerializer(many=True)
