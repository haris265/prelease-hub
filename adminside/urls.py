from django.urls import path, include
from rest_framework.routers import DefaultRouter
from adminside.views import (
    PropertyInquiryViewSet,
    PropertyListingViewSet
)

router = DefaultRouter()
router.register(r'property/inquiry', PropertyInquiryViewSet, basename='property/inquiry')
router.register(r'property/listing', PropertyListingViewSet, basename='property/listing')

urlpatterns = [
    path('', include(router.urls)),
]
