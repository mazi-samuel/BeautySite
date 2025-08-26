from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # KYC Review
    path('kyc/', views.kyc_review, name='kyc_review'),
    path('kyc/<int:kyc_id>/', views.kyc_review_detail, name='kyc_review_detail'),
    
    # Product Approval
    path('products/', views.product_approval, name='product_approval'),
    path('products/<int:product_id>/', views.product_review_detail, name='product_review_detail'),
    
    # Community Moderation
    path('community/', views.community_moderation, name='community_moderation'),
    path('community/reports/<int:report_id>/', views.handle_report, name='handle_report'),
    
    # Advertisement Management
    path('ads/', views.advertisement_management, name='advertisement_management'),
    path('ads/<int:ad_id>/', views.advertisement_detail, name='advertisement_detail'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
]
