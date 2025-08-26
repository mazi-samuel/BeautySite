from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.community.models import CommunityPost, CommunityMessage


class AdminAction(models.Model):
    ACTION_CHOICES = (
        ('user_activation', 'User Activation'),
        ('user_suspension', 'User Suspension'),
        ('product_approval', 'Product Approval'),
        ('product_rejection', 'Product Rejection'),
        ('kyc_approval', 'KYC Approval'),
        ('kyc_rejection', 'KYC Rejection'),
        ('content_removal', 'Content Removal'),
        ('user_ban', 'User Ban'),
        ('ad_approval', 'Ad Approval'),
        ('ad_rejection', 'Ad Rejection'),
    )
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    affected_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_actions')
    affected_post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, null=True, blank=True)
    affected_message = models.ForeignKey(CommunityMessage, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action_type}"


class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('post', 'Post'),
        ('message', 'Message'),
        ('user', 'User'),
        ('product', 'Product'),
    )
    
    REPORT_REASON_CHOICES = (
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('fraud', 'Fraud'),
        ('copyright', 'Copyright Infringement'),
        ('other', 'Other'),
    )
    
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    content_id = models.PositiveIntegerField()  # ID of the reported content
    report_reason = models.CharField(max_length=20, choices=REPORT_REASON_CHOICES)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='resolved_reports')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Report by {self.reported_by.username} - {self.report_type}"


class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.key
