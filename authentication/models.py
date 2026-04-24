import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.validators import FileExtensionValidator


# Create your models here.

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         extra_fields.setdefault("role", UserModel.Role.SUPER_ADMIN)
#         return self.create_user(email, password, **extra_fields)

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_no, password=None, **extra_fields):
        if not phone_no:
            raise ValueError("The Phone Number field must be set")
        extra_fields.pop('username', None)        
        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)
            
        user = self.model(phone_no=phone_no, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_no, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # Agar default role Super Admin set karna ho:
        extra_fields.setdefault("role", self.model.Role.SUPER_ADMIN)
        extra_fields.pop('username', None)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get("is_superuser") is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_no, password, **extra_fields)
        
        
class UserModel(AbstractUser):
    
    class Role(models.IntegerChoices):
        SUPER_ADMIN = 0, 'Super Admin'         
        BUYER = 1, 'Buyer' 
        SELLER = 2, 'Seller' 
        LEASER = 3, 'Leaser' 

                        
    first_name = None 
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=50, verbose_name="User Name", blank=True, null=True)
    last_name = models.CharField(max_length=50, verbose_name="Last Name", blank=True, null=True)    
    email = models.CharField(max_length=255, unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=255, verbose_name="Password", blank=True, null=True)
    phone_no = models.CharField(max_length=15, unique=True, verbose_name="Phone Number", blank=True, null=True)
    role = models.IntegerField(choices=Role.choices, verbose_name="Role Name", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    otp = models.IntegerField(blank=True, null=True)
    otp_status = models.BooleanField(default=False)
    otp_count = models.IntegerField(default=0)    
    # is_premium = models.BooleanField(default=False)
    # parking_task_id = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(
        upload_to='profile/image/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Profile Image", default="/profile/image/1.jpg"
    )
    def save(self, *args, **kwargs):
        """Password is hashed before saving"""
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    # USERNAME_FIELD = "email"
    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()
        
    
    def __str__(self):
            return self.email
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        

class UserWhitelistTokenModel(models.Model):
    """Model representing hashed whitelist tokens for user authentication"""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="whitelist_tokens", blank=True, null=True)
    token_fingerprint = models.CharField(blank=False,null=False,default="e99a18c428cb38d5f",max_length=64, unique=True, verbose_name="Token Fingerprint")
    refresh_token_fingerprint = models.CharField(blank=False,null=False,default="e99a18c428cb38d5f",max_length=64, unique=True, verbose_name="Refresh Token Fingerprint")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Token for {self.user.email}"  

    class Meta:
        verbose_name = "User Whitelist Token"
        verbose_name_plural = "User Whitelist Tokens"
        ordering = ["user"]



        




