from django.urls import path, include
from rest_framework.routers import DefaultRouter
from adminside.views import (
    PropertyInquiryViewSet
)

router = DefaultRouter()
router.register(r'property/inquiry', PropertyInquiryViewSet, basename='property/inquiry')

urlpatterns = [
    path('', include(router.urls)),
]
