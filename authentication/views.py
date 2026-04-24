import os
import random
from django.shortcuts import render
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permission.user_permission import UserGeneralAuthorization
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND
)
from core.helpers import handle_serializer_exception
from core.jwt_token import generate_jwt_payload
from .serializer import (
    UserLoginSerializer, 
    UserSignupSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    UserChangePasswordSerializer,
    
)
from authentication.models import UserModel

# Create your views here.
CLIENT_JWT_KEY = os.getenv('CLIENT_JWT_KEY')
"""JWT Token"""

class UserAuthViewSet(ModelViewSet):
    @action(detail=False, methods=['post'], permission_classes=[UserGeneralAuthorization])
    def deactivate_account(self, request):
        try:
            user = request.user_instance
            if not user.is_active:
                return Response({
                    "status": False,
                    "message": "Account is already deactivated."
                }, status=HTTP_400_BAD_REQUEST)

            user.is_active = False
            user.save()

            return Response({
                "status": True,
                "message": "Your account has been deactivated successfully.",
                # "data": {}
            }, status=HTTP_200_OK)

        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    # @action(detail= False,methods= ['POST']) 
    # def register(self, request):
    #     try:
    #         user_seriralizer = UserSignupSerializer(data = request.data)
    #         if not user_seriralizer.is_valid():
    #             return Response ({
    #                 "status": False,
    #                 "message": handle_serializer_exception(user_seriralizer)
    #             },status= HTTP_400_BAD_REQUEST)
    #         user_instance = user_seriralizer.save()
    #         token_payload = generate_jwt_payload(
    #             entity_instance = user_instance,
    #             roles = user_instance.role,
    #             jwt_key = CLIENT_JWT_KEY
    #         )
    #         if not token_payload["status"]:
    #             user_instance.delete()
    #             return Response ({
    #                 "status": False,
    #                 "message": token_payload["message"],
    #                 "details": token_payload["details"]
    #             },status= HTTP_500_INTERNAL_SERVER_ERROR)
    #         response_data = user_seriralizer.data
    #         if user_instance.date_joined:
    #             response_data['created_at'] = user_instance.date_joined
    #         else:
    #             response_data['created_at'] = None
    #         return Response ({
    #             "status": True,
    #             "message": "User created successfully",
    #             "access_token": token_payload["access_token"],
    #             "refresh_token": token_payload["refresh_token"],
    #             # "data": user_seriralizer.data
    #             "data": response_data
    #         },status= HTTP_200_OK)
    #     except Exception as swr:
    #         return Response({
    #             "status": False, 
    #             "message": str(swr)
    #         },status=HTTP_500_INTERNAL_SERVER_ERROR,)

    @action(detail=False, methods=['POST'])
    def register(self, request):
        try:
            user_serializer = UserSignupSerializer(data=request.data)
            if not user_serializer.is_valid():
                return Response({
                    "status": False,
                    "message": handle_serializer_exception(user_serializer)
                }, status=HTTP_400_BAD_REQUEST)
            
            user_instance = user_serializer.save()
            # user_instance.is_active = False
            # otp = random.randint(10000, 99999)  
            # user_instance.otp = str(otp) 
            # user_instance.save()
            
            # subject = "Welcome! Your Verification Code"
            # html_message = render_to_string('emails/register_otp_email.html', {
            #     'first_name': user_instance.first_name,
            #     'otp': otp
            # })
            # plain_message = strip_tags(html_message)
            # recipient = [user_instance.email]
            # send_mail(
            #     subject=subject,
            #     message=plain_message,          
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=recipient,
            #     html_message=html_message,      
            #     fail_silently=False,
            # )

            return Response({
                "status": True,
                "message": "User registered successfully.",
                "data": {"email": user_instance.email}
            }, status=HTTP_201_CREATED)

        except Exception as swr:
            if 'user_instance' in locals() and user_instance:
                user_instance.delete()
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['POST'])
    def register_verify_otp(self, request):
        email = request.data.get('email')
        provided_otp = request.data.get('otp')

        if not email or not provided_otp:
            return Response({
                "status": False, 
                "message": "Email and OTP are required."
            }, status=HTTP_400_BAD_REQUEST)

        try:
            user_instance = UserModel.objects.get(email=email)

            if str(user_instance.otp) == str(provided_otp):
                
                user_instance.is_active = True
                user_instance.otp = None  
                user_instance.save()

                return Response({
                    "status": True,
                    "message": "Account verified successfully. You can now log in.",
                    "redirect_to": "login"
                }, status=HTTP_200_OK)
            else:
                return Response({
                    "status": False, 
                    "message": "Invalid OTP. Please try again."
                }, status=HTTP_400_BAD_REQUEST)

        except UserModel.DoesNotExist:
            return Response({
                "status": False, 
                "message": "User not found."
            }, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": False, 
                "message": str(e)
            }, status=HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail= False,methods= ['POST'])
    def login(self, request):
        try:
            user_instance = UserLoginSerializer(data=request.data)
            print(user_instance)
            if not user_instance.is_valid():
                error = handle_serializer_exception(user_instance)
                return Response({"status":False,"message":error}, status=HTTP_400_BAD_REQUEST)
            
            user_data = user_instance.validated_data
            token_payload = generate_jwt_payload(
                entity_instance = user_data,
                roles = "Client",
                jwt_key = CLIENT_JWT_KEY
            )
            
            message = (
                "Buyer login successfully" if user_data.role == 1 else
                "Seller login successfully" if user_data.role == 2 else
                "Leaser login successfully" if user_data.role == 3 else
                "Admin login successfully"
            )

            response_data = {
                "id": user_data.id,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "email": user_data.email,
                "role": user_data.role,
                "image": user_data.image.url if user_data.image else None,
                "is_active": user_data.is_active
            }
            return Response (
                    {
                        "status": True,
                        "message": message,
                        "access_token": token_payload["access_token"],
                        "refresh_token": token_payload["refresh_token"],
                        "data": {
                            "id":user_data.id,
                            "user_name":user_data.user_name,
                            # "last_name":user_data.last_name,
                            "email":user_data.email,
                            "role":user_data.role,
                            "image": user_data.image.url if user_data.image else None,
                            "is_active":user_data.is_active,
                            # "is_paid": user_data.is_premium
                        }
                    },
                    status= HTTP_200_OK
                )  

        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=["POST"])
    def send_reset_email(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                error = handle_serializer_exception(serializer)
                return Response(
                    {"status": False, "message": error},
                    status=HTTP_400_BAD_REQUEST,
                )  
            
            # Generate OTP and update user
            otp = random.randint(10000, 99999)  # Ensures exactly 5 digits
            
            user = serializer.user
            user.otp = otp
            user.save()

            subject = "Your Password Reset Code"
            
            html_message = render_to_string('emails/otp_email.html', {
                'first_name': user.first_name,
                'otp': otp
            })
            
            plain_message = strip_tags(html_message)
            
            recipient = [user.email]
            
            send_mail(
                subject=subject,
                message=plain_message,          # Fallback plain text
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient,
                html_message=html_message,      # Asli HTML message
                fail_silently=False,
            )
            
            # "statue" typo fixed to "status"
            return Response({"status": True, "message": "Password reset email sent."}, status=HTTP_200_OK)
        
        except Exception as error:
            return Response(
                {"status": False, "error": str(error)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=["POST"])
    def verify_otp(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            if not serializer.is_valid():
                error = handle_serializer_exception(serializer)
                return Response(
                    {"status": False, "message": error},
                    status=HTTP_400_BAD_REQUEST
                )
            return Response(
                    {"status": True, "message": "OTP verified successfully"},
                    status=HTTP_200_OK,
                )
        except Exception as error:
            return Response(
                {"status": False, "error": str(error)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=["POST"])
    def reset_password(self, request):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                error = handle_serializer_exception(serializer)
                return Response(
                    {"status": False, "message": error},
                    status=HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                {"status": True, "message": "Password updated successfully."},
                status=HTTP_200_OK,
            )
        except Exception as error:
            return Response(
                {"status": False, "error": str(error)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=['POST'], permission_classes=[UserGeneralAuthorization])
    def change_password(self, request):
        serializer = UserChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Password changed successfully."}, status=HTTP_200_OK)
        return Response({"status": False, "errors": handle_serializer_exception(serializer)}, status=HTTP_400_BAD_REQUEST)
    
   