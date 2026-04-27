from django.db import models


class PropertyType(models.IntegerChoices):
    HOTEL = 1, 'Hotel'
    RESORT = 2, 'Resort'
    VILLA = 3, 'Villa'
    SERVICE_APARTMENT = 4, 'Service Apartment'
    HOLIDAY_HOME = 5, 'Holiday Home'


class IntentType(models.IntegerChoices):
    SELL = 1, 'Sell'
    LEASE = 2, 'Lease'
    BOTH = 3, 'Both'


class InquiryStatus(models.IntegerChoices):
    PENDING_ADMIN = 1, 'Pending Admin Approval'
    FORWARDED_TO_SELLER = 2, 'Forwarded to Seller'
    SELLER_REQUESTED_MEET = 3, 'Seller Requested Meet'
    MEETING_SCHEDULED = 4, 'Meeting Scheduled'
    REJECTED = 5, 'Rejected'





