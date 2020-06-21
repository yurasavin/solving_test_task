from rest_framework import viewsets

from sample.plans.models import Plan
from sample.plans.serializers import PlanSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset that provides `retrieve` and `list` actions.
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer