from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
    
    # Seller Dashboard
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/products/create/', views.create_product, name='create_product'),
    path('seller/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('seller/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
]
