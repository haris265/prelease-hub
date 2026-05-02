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
from adminside.serializer import(
    BuyerPropertyInquirySerializer
)
from user.serializer import(
    PropertyDocumentSerializer,
    PropertyListingSerializer
)
from user.models import (
    PropertyInquiryModel,
    PropertyListingModel,
    PropertyDocumentModel,
    InquiryStatus
)
from authentication.models import UserModel

class PropertyInquiryViewSet(ModelViewSet):
    queryset = PropertyInquiryModel.objects.all()
    serializer_class = BuyerPropertyInquirySerializer
    @action(detail=False, methods=['GET'], permission_classes=[UserGeneralAuthorization])
    def all_buyer_inquiries(self, request):
        try:
            if request.user_instance.role != UserModel.Role.SUPER_ADMIN:
                return Response({"status": False, "message": "Access denied."}, status=HTTP_403_FORBIDDEN)

            inquiries = PropertyInquiryModel.objects.filter(buyer__role=UserModel.Role.BUYER).order_by('-created_at')
            serializer = BuyerPropertyInquirySerializer(inquiries, many=True)
            return Response({"status": True, "message": "All buyer inquiries", "data": serializer.data}, status=HTTP_200_OK)
        except Exception as swr:
            return Response({"status": False, "message": str(swr)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['PATCH'], permission_classes=[UserGeneralAuthorization])
    def handle_buyer_operator_lead(self, request):
        """
        API for Admin to Approve, Disapprove, or Send Meet Link for a Buyer (Operator) lead.
        Route: PATCH /api/.../inquiries/handle_operator_lead/
        """
        try:
            # 1. Check if user is Super Admin
            if request.user_instance.role != UserModel.Role.SUPER_ADMIN:
                return Response({
                    "status": False, 
                    "message": "Access denied. Only Admin can perform this action."
                }, status=HTTP_403_FORBIDDEN)

            # 2. Extract ID and action from body
            inquiry_id = request.data.get('id')
            action_type = request.data.get('action') 
            meet_link = request.data.get('meet_link')

            if not inquiry_id:
                return Response({
                    "status": False, 
                    "message": "Inquiry ID ('id') is required in the request body."
                }, status=HTTP_400_BAD_REQUEST)

            # 3. Fetch the inquiry
            inquiry = PropertyInquiryModel.objects.filter(id=inquiry_id).first()
            if not inquiry:
                return Response({
                    "status": False, 
                    "message": "Inquiry not found."
                }, status=HTTP_404_NOT_FOUND)
            
            # Optional: Ensure this is actually a Buyer/Operator lead
            # if inquiry.buyer.role != UserModel.Role.BUYER:
            #     return Response({
            #         "status": False, 
            #         "message": "This inquiry is not from an Operator (Buyer)."
            #     }, status=HTTP_400_BAD_REQUEST)

            # 4. Handle Action
            if action_type == 'approve':
                inquiry.status = InquiryStatus.FORWARDED_TO_SELLER
                message = "Buyer lead approved and forwarded to the seller."
                
            elif action_type == 'disapprove':
                inquiry.status = InquiryStatus.REJECTED
                message = "Buyer lead has been disapproved."
                
            elif action_type == 'send_link':
                if not meet_link:
                    return Response({
                        "status": False, 
                        "message": "meet_link is required when scheduling a meeting."
                    }, status=HTTP_400_BAD_REQUEST)
                
                inquiry.status = InquiryStatus.MEETING_SCHEDULED
                inquiry.meet_link = meet_link
                message = "Meeting scheduled and link attached successfully."
                
            else:
                return Response({
                    "status": False, 
                    "message": "Invalid action. Please use 'approve', 'disapprove', or 'send_link'."
                }, status=HTTP_400_BAD_REQUEST)

            inquiry.save()

            return Response({
                "status": True,
                "message": message,
                "data": {
                    "id": inquiry.id,
                    "status": inquiry.status,
                    "status_name": inquiry.get_status_display(),
                    "meet_link": inquiry.meet_link
                }
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['GET'], permission_classes=[UserGeneralAuthorization])
    def all_lessee_inquiries(self, request):
        try:
            if request.user_instance.role != UserModel.Role.SUPER_ADMIN:
                return Response({"status": False, "message": "Access denied."}, status=HTTP_403_FORBIDDEN)

            inquiries = PropertyInquiryModel.objects.filter(buyer__role=UserModel.Role.LEASER).order_by('-created_at')
            serializer = BuyerPropertyInquirySerializer(inquiries, many=True)
            return Response({"status": True, "message": "All lessee inquiries", "data": serializer.data}, status=HTTP_200_OK)
        except Exception as swr:
            return Response({"status": False, "message": str(swr)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['PATCH'], permission_classes=[UserGeneralAuthorization])
    def handle_lessee_operator_lead(self, request):
        """
        API for Admin to Approve, Disapprove, or Send Meet Link for a Buyer (Operator) lead.
        Route: PATCH /api/.../inquiries/handle_operator_lead/
        """
        try:
            # 1. Check if user is Super Admin
            if request.user_instance.role != UserModel.Role.SUPER_ADMIN:
                return Response({
                    "status": False, 
                    "message": "Access denied. Only Admin can perform this action."
                }, status=HTTP_403_FORBIDDEN)

            # 2. Extract ID and action from body
            inquiry_id = request.data.get('id')
            action_type = request.data.get('action') 
            meet_link = request.data.get('meet_link')

            if not inquiry_id:
                return Response({
                    "status": False, 
                    "message": "Inquiry ID ('id') is required in the request body."
                }, status=HTTP_400_BAD_REQUEST)

            # 3. Fetch the inquiry
            inquiry = PropertyInquiryModel.objects.filter(id=inquiry_id).first()
            if not inquiry:
                return Response({
                    "status": False, 
                    "message": "Inquiry not found."
                }, status=HTTP_404_NOT_FOUND)
            
            # Optional: Ensure this is actually a Buyer/Operator lead
            # if inquiry.buyer.role != UserModel.Role.BUYER:
            #     return Response({
            #         "status": False, 
            #         "message": "This inquiry is not from an Operator (Buyer)."
            #     }, status=HTTP_400_BAD_REQUEST)

            # 4. Handle Action
            if action_type == 'approve':
                inquiry.status = InquiryStatus.FORWARDED_TO_SELLER
                message = "Lessee lead approved and forwarded to the seller."
                
            elif action_type == 'disapprove':
                inquiry.status = InquiryStatus.REJECTED
                message = "Lessee lead has been disapproved."
                
            elif action_type == 'send_link':
                if not meet_link:
                    return Response({
                        "status": False, 
                        "message": "meet_link is required when scheduling a meeting."
                    }, status=HTTP_400_BAD_REQUEST)
                
                inquiry.status = InquiryStatus.MEETING_SCHEDULED
                inquiry.meet_link = meet_link
                message = "Meeting scheduled and link attached successfully."
                
            else:
                return Response({
                    "status": False, 
                    "message": "Invalid action. Please use 'approve', 'disapprove', or 'send_link'."
                }, status=HTTP_400_BAD_REQUEST)

            inquiry.save()

            return Response({
                "status": True,
                "message": message,
                "data": {
                    "id": inquiry.id,
                    "status": inquiry.status,
                    "status_name": inquiry.get_status_display(),
                    "meet_link": inquiry.meet_link
                }
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
    

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

class DashboardViewSet(ModelViewSet):
    """
    API to fetch total counts for the Admin Dashboard.
    Route: GET /adminside/v1/dashboard/counts/
    """
    @action(detail=False, methods=['GET'], permission_classes=[UserGeneralAuthorization])
    def dashboard_stats(self, request):
        try:
            # 1. Admin Authorization Check
            if request.user_instance.role != UserModel.Role.SUPER_ADMIN:
                return Response({
                    "status": False, 
                    "message": "Access Denied. Only Admin can view dashboard stats."
                }, status=HTTP_403_FORBIDDEN)

            total_users = UserModel.objects.count() 
            total_buyers = UserModel.objects.filter(role=UserModel.Role.BUYER).count()
            total_sellers = UserModel.objects.filter(role=UserModel.Role.SELLER).count()
            total_lessees = UserModel.objects.filter(role=UserModel.Role.LEASER).count()
            total_properties = PropertyListingModel.objects.count()

            # 4. Return Data
            return Response({
                "status": True,
                "message": "Dashboard stats retrieve successfully.",
                "data": {
                    "total_users": total_users,
                    "total_buyers": total_buyers,
                    "total_sellers": total_sellers,
                    "total_lessees": total_lessees,
                    "total_properties": total_properties
                }
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
   





