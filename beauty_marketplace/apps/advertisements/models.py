from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class Advertisement(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    target_url = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class AdvertisementSlot(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='slots')
    slot_name = models.CharField(max_length=100)
    page_location = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=50, blank=True)
    price_per_impression = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    price_per_click = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.slot_name} for {self.advertisement.title}"
