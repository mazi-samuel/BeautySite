from django.urls import path
from . import views

app_name = 'advertisements'

urlpatterns = [
    path('', views.ad_slots, name='ad_slots'),
    path('management/', views.advertisement_management, name='advertisement_management'),
    path('management/create/', views.create_advertisement, name='create_advertisement'),
    path('management/<int:ad_id>/', views.advertisement_detail, name='advertisement_detail'),
    path('management/<int:ad_id>/edit/', views.edit_advertisement, name='edit_advertisement'),
    path('management/<int:ad_id>/delete/', views.delete_advertisement, name='delete_advertisement'),
]
