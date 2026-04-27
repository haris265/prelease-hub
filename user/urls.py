from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import (
    PropertyListingViewSet,
    PropertyInquiryViewSet
)


router = DefaultRouter()
router.register(r'property/listing', PropertyListingViewSet, basename='property/listing')
router.register(r'property/inquiry', PropertyInquiryViewSet, basename='property/inquiry')

urlpatterns = [
    path('', include(router.urls)),
]
