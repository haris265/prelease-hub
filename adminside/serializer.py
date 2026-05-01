from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
    ValidationError
)
from user.models import (
    PropertyInquiryModel
)


class BuyerPropertyInquirySerializer(ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.user_name', read_only=True)
    property_name = serializers.CharField(source='property.property_name', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PropertyInquiryModel
        fields = [
            'id', 'property', 'property_name', 'buyer', 'buyer_name', 
            'status', 'meet_link', 'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'status', 'meet_link']



    