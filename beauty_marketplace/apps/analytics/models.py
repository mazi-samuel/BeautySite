from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.products.models import Product
from apps.orders.models import Order


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)  # e.g., 'login', 'product_view', 'add_to_cart'
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # null for anonymous users
    session_key = models.CharField(max_length=40, blank=True)  # for anonymous users
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"View of {self.product.name}"


class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # null for anonymous users
    query = models.CharField(max_length=200)
    result_count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Search: {self.query}"


class RevenueReport(models.Model):
    date = models.DateField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    order_count = models.PositiveIntegerField(default=0)
    product_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Revenue Report for {self.date}"
    
    class Meta:
        unique_together = ('date',)


class UserSignup(models.Model):
    date = models.DateField()
    signup_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Signups for {self.date}"
    
    class Meta:
        unique_together = ('date',)
