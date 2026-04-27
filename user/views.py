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
from user.serializer import(
    PropertyListingSerializer,
    PropertyDocumentSerializer,
    PropertyInquirySerializer
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

class PropertyInquiryViewSet(ModelViewSet):
    @action(detail=False, methods=['POST'], permission_classes=[UserGeneralAuthorization])
    def inquiry_create(self, request):
        try:
            # Check if user is buyer or leaser
            if request.user_instance.role not in [UserModel.Role.BUYER, UserModel.Role.LEASER]:
                return Response({
                    "status": False,
                    "message": "Only buyers or leasers can submit property inquiries."
                }, status=HTTP_403_FORBIDDEN)

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
            if request.user_instance.role not in [UserModel.Role.BUYER, UserModel.Role.LEASER]:
                return Response({
                    "status": False,
                    "message": "Only buyers or leasers can view their inquiries."
                }, status=HTTP_403_FORBIDDEN)

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
    
   





