from django.urls import path, include
from rest_framework.routers import DefaultRouter
from adminside.views import (
    PropertyInquiryViewSet,
    PropertyListingViewSet,
    DashboardViewSet,
    AdminUserViewSet
)

router = DefaultRouter()
router.register(r'property/inquiry', PropertyInquiryViewSet, basename='property/inquiry')
router.register(r'property/listing', PropertyListingViewSet, basename='property/listing')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'users', AdminUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
