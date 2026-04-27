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
    PropertyInquirySerializer
)
from user.models import (
    PropertyInquiryModel
)
from authentication.models import UserModel

class PropertyInquiryViewSet(ModelViewSet):
    queryset = PropertyInquiryModel.objects.all()
    serializer_class = PropertyInquirySerializer
    @action(detail=False, methods=['GET'], permission_classes=[UserGeneralAuthorization])
    def all_inquiries(self, request):
        try:
            if request.user_instance.role != UserModel.Role.SUPER_ADMIN:
                return Response({"status": False, "message": "Access denied."}, status=HTTP_403_FORBIDDEN)

            inquiries = PropertyInquiryModel.objects.all().order_by('-created_at')
            serializer = PropertyInquirySerializer(inquiries, many=True)
            return Response({"status": True, "message": "All inquiries fetched.", "data": serializer.data}, status=HTTP_200_OK)
        except Exception as swr:
            return Response({"status": False, "message": str(swr)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
   





