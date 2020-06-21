from rest_framework import serializers

from sample.sprint_subscriptions.models import SprintSubscription


class SprintSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SprintSubscription
        fields = '__all__'


class SprintAggregateByPriceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    data_excess = serializers.DecimalField(decimal_places=4, max_digits=20)
    voice_excess = serializers.DecimalField(decimal_places=4, max_digits=20)

    class Meta:
        model = SprintSubscription
        fields = ['id', 'data_excess', 'voice_excess']


class SprintAggregateByDateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    total_usage = serializers.DecimalField(decimal_places=4, max_digits=20)
    date_usage = serializers.DecimalField(decimal_places=4, max_digits=20)

    class Meta:
        model = SprintSubscription
        fields = ['id', 'total_usage', 'date_usage']
