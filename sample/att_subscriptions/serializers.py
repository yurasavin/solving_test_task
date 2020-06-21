from rest_framework import serializers

from sample.att_subscriptions.models import ATTSubscription


class ATTSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ATTSubscription
        fields = "__all__"


class ATTAggregateByPriceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    data_excess = serializers.DecimalField(decimal_places=4, max_digits=20)
    voice_excess = serializers.DecimalField(decimal_places=4, max_digits=20)

    class Meta:
        model = ATTSubscription
        fields = ['id', 'data_excess', 'voice_excess']


class ATTAggregateByDateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    total_usage = serializers.DecimalField(decimal_places=4, max_digits=20)
    date_usage = serializers.DecimalField(decimal_places=4, max_digits=20)

    class Meta:
        model = ATTSubscription
        fields = ['id', 'total_usage', 'date_usage']
