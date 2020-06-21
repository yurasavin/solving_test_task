from django.db.models import Case, DecimalField, F, Q, Sum, Value, When
from django.utils.functional import cached_property

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from sample.aggregated_usage.serializers import (
    AggregatedUsageByDateSerializer, AggregatedUsageByPriceSerializer,
    DateParamSerializer, PriceParamSerializer)
from sample.att_subscriptions.models import ATTSubscription
from sample.sprint_subscriptions.models import SprintSubscription


class AggregatedUsageByPriceView(viewsets.GenericViewSet):
    """
    A viewset that provides only `list` action.
    """
    serializer_class = AggregatedUsageByPriceSerializer

    @cached_property
    def price_param(self):
        """
        Get and cache `price` param from request query string
        """
        price = self.request.query_params.get('price')

        if not price:
            raise ValidationError({'price': ['This parameter is required.']})

        serializer = PriceParamSerializer(data={'price': price})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['price']

    def get_querysets(self):
        att_queryset = ATTSubscription.objects.annotate(
            total_data_price=Sum('aggregateddatausage__price', distinct=True),
            total_voice_price=Sum('aggregatedvoiceusage__price', distinct=True),  # noqa: E501
        )

        sprints_queryset = SprintSubscription.objects.annotate(
            total_data_price=Sum('aggregateddatausage__price', distinct=True),
            total_voice_price=Sum('aggregatedvoiceusage__price', distinct=True),  # noqa: E501
        )

        return att_queryset, sprints_queryset

    def filter_qs_by_price_gt(self, att_queryset, sprints_queryset):
        """
        Filter querysets by price
        """
        price = self.price_param
        query = Q(total_data_price__gt=price) | Q(total_voice_price__gt=price)
        att_queryset = att_queryset.filter(query)
        sprints_queryset = sprints_queryset.filter(query)

        return att_queryset, sprints_queryset

    def annotate_excess_to_qs(self, att_queryset, sprints_queryset):
        """
        Annotates for querysets excess of the price, by usage type
        """
        price = self.price_param

        att_queryset = att_queryset\
            .annotate(
                data_excess=F('total_data_price') - price,
                voice_excess=F('total_voice_price') - price)\
            .annotate(
                data_excess=Case(
                    When(data_excess__gt=0, then='data_excess'),
                    default=Value(None),
                    output_field=DecimalField(null=True),
                ),
                voice_excess=Case(
                    When(voice_excess__gt=0, then='voice_excess'),
                    default=Value(None),
                    output_field=DecimalField(null=True),
                ),
            )

        sprints_queryset = sprints_queryset\
            .annotate(
                data_excess=F('total_data_price') - price,
                voice_excess=F('total_voice_price') - price)\
            .annotate(
                data_excess=Case(
                    When(data_excess__gt=0, then='data_excess'),
                    default=Value(None),
                    output_field=DecimalField(null=True),
                ),
                voice_excess=Case(
                    When(voice_excess__gt=0, then='voice_excess'),
                    default=Value(None),
                    output_field=DecimalField(null=True),
                ),
            )

        return att_queryset, sprints_queryset

    def list(self, request, *args, **kwargs):
        att_qs, sprints_qs = self.filter_qs_by_price_gt(*self.get_querysets())
        att_qs, sprints_qs = self.annotate_excess_to_qs(att_qs, sprints_qs)

        values = ['id', 'data_excess', 'voice_excess']
        data = {
            'att_subscriptions': att_qs.values(*values),
            'sprint_subscriptions': sprints_qs.values(*values),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class AggregatedUsageByDateView(viewsets.GenericViewSet):
    """
    A viewset that provides only `list` action.
    """
    serializer_class = AggregatedUsageByDateSerializer

    @cached_property
    def from_date_param(self):
        """
        Get and cache `from_date` param from request query string
        """
        from_date = self.request.query_params.get('from_date')

        if not from_date:
            raise ValidationError({'from_date': ['This parameter is required.']})  # noqa: E501

        serializer = DateParamSerializer(data={'date': from_date})
        serializer.is_valid(raise_exception=True)
        from_date = serializer.validated_data['date']

        to_date = self.to_date_param

        if to_date < from_date:
            raise ValidationError({'from_date': ['This parameter cant be greater then `to_date`.']})  # noqa: E501

        return from_date

    @cached_property
    def to_date_param(self):
        """
        Get and cache `to_date` param from request query string
        """
        to_date = self.request.query_params.get('to_date')

        if not to_date:
            raise ValidationError({'to_date': ['This parameter is required.']})

        serializer = DateParamSerializer(data={'date': to_date})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['date']

    @cached_property
    def usage_type_param(self):
        """
        Get and cache `usage_type` param from request query string
        """
        usage_type = self.request.query_params.get('usage_type')

        if not usage_type:
            raise ValidationError({'usage_type': ['This parameter is required.']})  # noqa: E501

        if usage_type == 'data':
            return 'data'
        elif usage_type == 'voice':
            return 'voice'

        raise ValidationError({'usage_type': ['Availible choices: ["data", "voice"].']})  # noqa: E501

    def get_querysets(self):
        att_queryset = ATTSubscription.objects.all()
        sprints_queryset = SprintSubscription.objects.all()

        return att_queryset, sprints_queryset

    def annotate_total_usage_to_qs(self, att_queryset, sprints_queryset):
        """
        Annotates for querysets `total_usage` value
        """
        usage_type = self.usage_type_param

        if usage_type == 'data':
            query = Sum('aggregateddatausage__price')
        elif usage_type == 'voice':
            query = Sum('aggregatedvoiceusage__price')

        att_queryset = att_queryset.annotate(total_usage=query)
        sprints_queryset = sprints_queryset.annotate(total_usage=query)
        return att_queryset, sprints_queryset

    def annotate_date_usage_to_qs(self, att_queryset, sprints_queryset):
        """
        Annotates for querysets `date_usage` value
        """
        date_range = (self.from_date_param, self.to_date_param)
        usage_type = self.usage_type_param

        if usage_type == 'data':
            query = Sum(
                'aggregateddatausage__price',
                filter=Q(aggregateddatausage__usage_date__range=date_range),
            )
        elif usage_type == 'voice':
            query = Sum(
                'aggregatedvoiceusage__price',
                filter=Q(aggregatedvoiceusage__usage_date__range=date_range),
            )

        att_queryset = att_queryset.annotate(date_usage=query)
        sprints_queryset = sprints_queryset.annotate(date_usage=query)
        return att_queryset, sprints_queryset

    def exclude_null_date_usage_from_qs(self, att_queryset, sprints_queryset):
        """
        Excludes from queryset rows with null `date_usage`
        """
        att_queryset = att_queryset.exclude(date_usage__isnull=True)
        sprints_queryset = sprints_queryset.exclude(date_usage__isnull=True)
        return att_queryset, sprints_queryset

    def list(self, request, *args, **kwargs):
        att_qs, sprints_qs = self.get_querysets()
        att_qs, sprints_qs = self.annotate_total_usage_to_qs(att_qs, sprints_qs)  # noqa: E501
        att_qs, sprints_qs = self.annotate_date_usage_to_qs(att_qs, sprints_qs)
        att_qs, sprints_qs = self.exclude_null_date_usage_from_qs(att_qs, sprints_qs)  # noqa: E501

        values = ['id', 'total_usage', 'date_usage']
        data = {
            'att_subscriptions': att_qs.values(*values),
            'sprint_subscriptions': sprints_qs.values(*values),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
