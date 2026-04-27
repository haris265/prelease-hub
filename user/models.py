import uuid
from django.db import models
from django.contrib.auth.hashers import make_password
from core.choices import (
    PropertyType,  
    IntentType,
    InquiryStatus
)
from django.core.validators import ( 
    MinValueValidator, 
    MaxValueValidator
)
from authentication.models import UserModel


# Create your models here.

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class PropertyListingModel(BaseModel):
    # Contact & Basic Info
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE, 
        related_name='property_listings',
        blank=True,
        null=True
    )
    owner_company_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField()
    property_name = models.CharField(max_length=255)
    
    # Location & Type
    property_type = models.IntegerField(
        choices=PropertyType.choices,
        # default=PropertyType.HOTEL
    )
    city = models.CharField(max_length=100)
    full_address = models.TextField()
    
    # Financials & Specs
    intent = models.IntegerField(
        choices=IntentType.choices,
        # default=IntentType.SELL
    )
    expected_price_rent = models.DecimalField(max_digits=15, decimal_places=2) 
    rooms_keys = models.PositiveIntegerField(blank=True,
        null=True)
    
    current_occupancy_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage from 0 to 100",
        blank=True,
        null=True
    )
    current_monthly_income = models.DecimalField(max_digits=15, decimal_places=2, blank=True,null=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.property_name} ({self.get_intent_display()}) - {self.owner_company_name}"
    
    class Meta:
        verbose_name = "Property Listing"
        verbose_name_plural = "Property Listings"


class PropertyDocumentModel(BaseModel):
    property_listing = models.ForeignKey(
        PropertyListingModel, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_file = models.FileField(upload_to='property_documents/%Y/%m/')

    
    def __str__(self):
        return f"Document for {self.property_listing.property_name}"
    
    class Meta:
        verbose_name = "Property Document"
        verbose_name_plural = "Property Documents"


class PropertyInquiryModel(BaseModel):
    property = models.ForeignKey(
        PropertyListingModel, 
        on_delete=models.CASCADE, 
        related_name='inquiries'
    )
    buyer = models.ForeignKey(
        UserModel, 
        on_delete=models.CASCADE, 
        related_name='my_inquiries'
    )
    status = models.IntegerField(
        choices=InquiryStatus.choices, 
        default=InquiryStatus.PENDING_ADMIN
    )
    meet_link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Inquiry by {self.buyer.user_name} for {self.property.property_name}"
    
    class Meta:
        verbose_name = "Property Inquiry"
        verbose_name_plural = "Property Inquiries"
        ordering = ['-created_at']






        




