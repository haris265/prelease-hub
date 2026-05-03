from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.permission.user_permission import UserGeneralAuthorization
from core.helpers import handle_serializer_exception
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from core.choices import (
    ListingStatus,
    InquiryStatus
)
from user.serializer import(
    PropertyListingSerializer,
    PropertyDocumentSerializer,
    PropertyInquirySerializer
)
from adminside.serializer import(
    BuyerPropertyInquirySerializer
)
from user.models import (
    PropertyListingModel,
    PropertyDocumentModel,
    PropertyInquiryModel
)
from authentication.models import UserModel

class PropertyListingViewSet(ModelViewSet):
    @action(detail= False,methods= ['POST'],permission_classes=[UserGeneralAuthorization]) 
    def property_create(self, request):
        try:
            user = request.user_instance
            listing = PropertyListingSerializer(data = request.data)
            if not listing.is_valid():
                return Response ({
                    "status": False,
                    "message": handle_serializer_exception(listing)
                    },status=status.HTTP_400_BAD_REQUEST)
            _ = listing.save(user=user)
            return Response ({
                "status": True,
                "message": "Property created successfully",
                "data": listing.data
                },status=status.HTTP_201_CREATED)
        except Exception as swr:
            return Response({
                "status": False, "message": str(swr)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR,)
    
    @action(detail= False,methods= ['GET'],permission_classes=[UserGeneralAuthorization]) 
    def property_view(self, request):
        try:
            user = request.user_instance
            listings = PropertyListingModel.objects.filter(user=user)
            serializer = PropertyListingSerializer(listings, many=True)
            return Response ({
                "status": True,
                "message": "Property retrieve successfully",
                "data": serializer.data
            })
        
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail= False,methods= ['GET']) 
    def approve_property_view(self, request):
        try:
            listings = PropertyListingModel.objects.filter(status=ListingStatus.APPROVED)
            serializer = PropertyListingSerializer(listings, many=True)
            return Response ({
                "status": True,
                "message": "Property retrieve successfully",
                "data": serializer.data
            })
        
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, url_path="property_delete/(?P<pk>[0-9a-f-]+)", methods=['DELETE'], permission_classes=[UserGeneralAuthorization])
    def property_delete(self, request, pk=None):
        try:
            listing = PropertyListingModel.objects.filter(id=pk).first()
            if not listing:
                return Response({
                    "status": False, "message": "property not found"
                    },status=status.HTTP_404_NOT_FOUND)
            listing.delete()
            return Response({
                "status": True,
                "message": "Property     deleted successfully"
                },status=status.HTTP_200_OK)
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=['PATCH'], permission_classes=[UserGeneralAuthorization])
    def property_update(self, request):
        try:
            listing_id = request.data.get('id')
            listing = PropertyListingModel.objects.filter(id=listing_id).first()
            if not listing:
                return Response(
                    {"status": False, "message": "property not found to update it."},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = PropertyListingSerializer(instance=listing, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "message": handle_serializer_exception(serializer)
                },status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(
                {   
                "status": True,
                "message": "Property updated successfully",
                "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=['GET']) # Public API
    def filter_properties(self, request):
        """
        Simple GET API for filtering properties based on 4 parameters.
        Route: GET /api/.../property/listing/filter_properties/
        """
        try:
            queryset = PropertyListingModel.objects.filter(status=ListingStatus.APPROVED)

            location = request.query_params.get('location')
            property_type = request.query_params.get('property_type')
            listing_type = request.query_params.get('listing_type')
            area = request.query_params.get('area')

            if location:
                queryset = queryset.filter(location__icontains=location)
            
            if property_type:
                queryset = queryset.filter(property_type=property_type)
            
            if listing_type:
                queryset = queryset.filter(listing_type=listing_type)
            
            if area:
                queryset = queryset.filter(built_up_area__gte=area)

            queryset = queryset.order_by('-created_at')

            serializer = PropertyListingSerializer(queryset, many=True)
            
            return Response({
                "status": True,
                "message": f"{queryset.count()} properties found.",
                "data": serializer.data
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)

class PropertyInquiryViewSet(ModelViewSet):
    @action(detail=False, methods=['POST'], permission_classes=[UserGeneralAuthorization])
    def inquiry_create(self, request):
        try:
            # Check if user is buyer or leaser
            # if request.user_instance.role not in [UserModel.Role.BUYER, UserModel.Role.LEASER]:
            #     return Response({
            #         "status": False,
            #         "message": "Only buyers or leasers can submit property inquiries."
            #     }, status=HTTP_403_FORBIDDEN)

            serializer = PropertyInquirySerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "message": handle_serializer_exception(serializer)
                }, status=HTTP_400_BAD_REQUEST)
            
            inquiry_instance = serializer.save(buyer=request.user_instance)

            return Response({
                "status": True,
                "message": "Inquiry submitted successfully. Pending Admin verification.",
                "data": {"id": inquiry_instance.id, "status": inquiry_instance.status}
            }, status=HTTP_201_CREATED)

        except Exception as swr:
            if 'inquiry_instance' in locals() and inquiry_instance:
                inquiry_instance.delete()
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['GET'], permission_classes=[UserGeneralAuthorization])
    def my_inquiries(self, request):
        """
        Dashboard API for Buyer/Leaser to view their own property requests.
        Route: GET /api/inquiries/my_inquiries/
        """
        try:
            # Check if user is buyer or leaser
            # if request.user_instance.role not in [UserModel.Role.BUYER, UserModel.Role.LEASER]:
            #     return Response({
            #         "status": False,
            #         "message": "Only buyers or leasers can view their inquiries."
            #     }, status=HTTP_403_FORBIDDEN)

            # Filter inquiries where the current user is the buyer
            # order_by('-created_at') se latest request sabse upar aayegi
            inquiries = PropertyInquiryModel.objects.filter(buyer=request.user_instance).order_by('-created_at')
            
            # Data serialize karein
            serializer = PropertyInquirySerializer(inquiries, many=True)

            return Response({
                "status": True,
                "message": "My inquiries retrieve successfully.",
                "data": serializer.data
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['GET'], permission_classes=[UserGeneralAuthorization])
    def seller_received_inquiries(self, request):
        """
        API for Seller to view inquiries forwarded by Admin.
        Route: GET /api/.../inquiries/seller_received_inquiries/
        """
        try:
            # 1. Ensure the user is a Seller
            # if request.user_instance.role != UserModel.Role.SELLER:
            #     return Response({
            #         "status": False,
            #         "message": "Access denied. Only Sellers can view these inquiries."
            #     }, status=HTTP_403_FORBIDDEN)

            # 2. Define the statuses that a seller is allowed to see
            # (Admin se forwarded, Seller ne meet request ki, ya Meeting schedule ho gayi)
            allowed_statuses = [
                InquiryStatus.FORWARDED_TO_SELLER,
                InquiryStatus.SELLER_REQUESTED_MEET,
                InquiryStatus.MEETING_SCHEDULED
            ]

            # 3. Filter the inquiries
            # property__user: Ye check karta hai ke inquiry jis property par hai, uska owner current user ho
            # status__in: Ye ensure karta hai ke sirf approved requests hi aayen (Pending Admin wali nahi)
            inquiries = PropertyInquiryModel.objects.filter(
                property__user=request.user_instance,
                status__in=allowed_statuses
            ).order_by('-updated_at')  # Latest updated requests sabse upar

            # 4. Serialize data
            # Yahan apna main serializer use karein jo aapne query mein define kiya hai
            serializer = BuyerPropertyInquirySerializer(inquiries, many=True)

            return Response({
                "status": True,
                "message": "Forwarded inquiries retrieved successfully for seller.",
                "data": serializer.data
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['PATCH'], permission_classes=[UserGeneralAuthorization])
    def seller_request_meeting(self, request):
        """
        API for Seller to request Admin to schedule a meeting with the Buyer.
        Route: PATCH /user/v1/property/inquiry/seller_request_meeting/
        """
        try:
            # 1. Ensure the user is a Seller
            # if request.user_instance.role != UserModel.Role.SELLER:
            #     return Response({
            #         "status": False,
            #         "message": "Access denied. Only Sellers can request a meeting."
            #     }, status=HTTP_403_FORBIDDEN)

            # 2. Get Inquiry ID from body
            inquiry_id = request.data.get('id')
            if not inquiry_id:
                return Response({
                    "status": False, 
                    "message": "Inquiry ID ('id') is required."
                }, status=HTTP_400_BAD_REQUEST)

            inquiry = PropertyInquiryModel.objects.filter(
                id=inquiry_id, 
                property__user=request.user_instance 
            ).first()

            if not inquiry:
                return Response({
                    "status": False, 
                    "message": "Inquiry not found or you do not have permission to modify it."
                }, status=HTTP_404_NOT_FOUND)

            if inquiry.status != InquiryStatus.FORWARDED_TO_SELLER:
                return Response({
                    "status": False,
                    "message": f"You cannot request a meeting at this stage. Current status: {inquiry.get_status_display()}"
                }, status=HTTP_400_BAD_REQUEST)

            inquiry.status = InquiryStatus.SELLER_REQUESTED_MEET
            inquiry.save()

            return Response({
                "status": True,
                "message": "Meeting request sent to Admin successfully.",
                "data": {
                    "id": inquiry.id,
                    "status": inquiry.status,
                    "status_name": inquiry.get_status_display()
                }
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
   





