from django.contrib import admin
from user.models import (
    PropertyListingModel, 
    PropertyDocumentModel,
    PropertyInquiryModel
) 


# Register your models here.
admin.site.register(PropertyListingModel)
admin.site.register(PropertyDocumentModel)
admin.site.register(PropertyInquiryModel)




