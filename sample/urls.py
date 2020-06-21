"""sample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from rest_framework import routers

from sample.aggregated_usage.views import (AggregatedUsageByDateView,
                                           AggregatedUsageByPriceView)
from sample.att_subscriptions.views import ATTSubscriptionViewSet
from sample.plans.views import PlanViewSet
from sample.purchases.views import PurchaseViewSet
from sample.sprint_subscriptions.views import SprintSubscriptionViewSet

router = routers.DefaultRouter()

router.register(r'aggregated-usage-by-price', AggregatedUsageByPriceView, basename='aggregated-usage-by-price')
router.register(r'aggregated-usage-by-date', AggregatedUsageByDateView, basename='aggregated-usage-by-date')
router.register(r'att-subscriptions', ATTSubscriptionViewSet)
router.register(r'plans', PlanViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'sprint-subscriptions', SprintSubscriptionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((router.urls, 'api'), namespace='api')),
]
