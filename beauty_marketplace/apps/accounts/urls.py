from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('change-password/', views.change_password, name='change_password'),
    path('kyc/submit/', views.kyc_submit, name='kyc_submit'),
    path('kyc/status/', views.kyc_status, name='kyc_status'),
    path('age-verification/', views.age_verification, name='age_verification'),
]
