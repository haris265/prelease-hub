from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
    ValidationError
)
from user.models import (
    PropertyInquiryModel,
    UserModel
)


# class BuyerPropertyInquirySerializer(ModelSerializer):
#     buyer_name = serializers.CharField(source='buyer.user_name', read_only=True)
#     property_name = serializers.CharField(source='property.property_name', read_only=True)
#     status = serializers.CharField(source='get_status_display', read_only=True)

#     class Meta:
#         model = PropertyInquiryModel
#         fields = [
#             'id', 'property', 'property_name', 'buyer', 'buyer_name', 
#             'status', 'meet_link', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['buyer', 'status', 'meet_link']


class BuyerPropertyInquirySerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)
    property_details = serializers.SerializerMethodField(read_only=True)
    buyer_details = serializers.SerializerMethodField(read_only=True)
    seller_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PropertyInquiryModel
        fields = [
            'id', 
            'property',          # ID for POST request
            'buyer',             # ID for internal linking
            'status',            # Status integer
            # 'status_name',       # Status String
            'meet_link', 
            'created_at', 
            'updated_at',
            
            # Nested fields for GET response
            'property_details',
            'buyer_details',
            'seller_details'
        ]
        
        read_only_fields = ['buyer', 'status', 'meet_link']

  
    
    def get_property_details(self, obj):
        from user.serializer import PropertyListingSerializer 
        
        if obj.property:
            return PropertyListingSerializer(obj.property).data
        return None

    def get_buyer_details(self, obj):
        from adminside.serializer import AdminUserSerializer
        
        if obj.buyer:
            return AdminUserSerializer(obj.buyer).data
        return None

    def get_seller_details(self, obj):
        from adminside.serializer import AdminUserSerializer
        
        if obj.property and obj.property.user:
            return AdminUserSerializer(obj.property.user).data
        return None


class AdminUserSerializer(ModelSerializer):
    role = CharField(source='get_role_display', read_only=True)
    class Meta:
        model = UserModel
        fields = ['id', 'user_name', 'email', 'phone_no', 'role', 'is_active', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}, 
            'email': {'required': True},
            'phone_no': {'required': True}
        }



    