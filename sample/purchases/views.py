from rest_framework import viewsets

from sample.purchases.models import Purchase
from sample.purchases.serializers import PurchaseSerializer


class PurchaseViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
