from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .managers import CustomUserManager


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    
    phone = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class UserKYC(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc')
    id_document_url = models.URLField(blank=True)
    selfie_url = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s KYC ({self.status})"


class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification')
    age_verified = models.BooleanField(default=False)
    age_verified_at = models.DateTimeField(null=True, blank=True)
    verification_token = models.CharField(max_length=100, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username}'s verification"
