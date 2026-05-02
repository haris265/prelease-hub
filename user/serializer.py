from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
    ValidationError
)
from user.models import (
    PropertyListingModel, 
    PropertyDocumentModel,
    PropertyInquiryModel
)

class PropertyDocumentSerializer(ModelSerializer):
    class Meta:
        model = PropertyDocumentModel
        fields = ['id', 'document_file']

class PropertyListingSerializer(ModelSerializer):
    # Read-only field to display saved documents
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    
    # Write-only field to accept multiple files during creation
    uploaded_documents = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = PropertyListingModel
        fields = [
            'id', 
            'user', 
            'property_name', 
            'city', 
            'location', 
            'property_type', 
            'rooms',                
            'built_up_area', 
            'listing_type',         
            'selling_price',        
            'expected_monthly_rent',
            'security_deposit',     
            'annual_rental_income', 
            'lock_in_period',      
            'owner_company_name',   
            'phone_number', 
            'email_address',
            'property_description',
            'status',
            'documents', 
            'uploaded_documents'
        ]

    def create(self, validated_data):
        # Extract uploaded files from the data
        uploaded_documents = validated_data.pop('uploaded_documents', [])
        
        # Create the main property listing
        listing = PropertyListingModel.objects.create(**validated_data)
        
        # Save each uploaded file in the PropertyDocument model
        for document in uploaded_documents:
            PropertyDocumentModel.objects.create(property_listing=listing, document_file=document)
            
        return listing


class PropertyInquirySerializer(ModelSerializer):
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



    