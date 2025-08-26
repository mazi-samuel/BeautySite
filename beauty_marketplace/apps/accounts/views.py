from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
import json

from .models import User, UserProfile, UserKYC, UserVerification
from .forms import UserRegistrationForm, UserProfileForm, PasswordChangeForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Please complete your profile.')
            return redirect('accounts:profile')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('products:home')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def upload_avatar(request):
    if request.method == 'POST':
        avatar_url = request.POST.get('avatar_url')
        if avatar_url:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            user_profile.avatar_url = avatar_url
            user_profile.save()
            messages.success(request, 'Avatar updated successfully.')
        else:
            messages.error(request, 'Please provide an avatar URL.')
    
    return render(request, 'accounts/upload_avatar.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def kyc_submit(request):
    user_kyc, created = UserKYC.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        id_document_url = request.POST.get('id_document_url')
        selfie_url = request.POST.get('selfie_url')
        
        if id_document_url and selfie_url:
            user_kyc.id_document_url = id_document_url
            user_kyc.selfie_url = selfie_url
            user_kyc.status = 'pending'
            user_kyc.save()
            
            messages.success(request, 'KYC documents submitted successfully. Please wait for verification.')
            return redirect('accounts:kyc_status')
        else:
            messages.error(request, 'Please provide both ID document and selfie.')
    
    return render(request, 'accounts/kyc_submit.html')


@login_required
def kyc_status(request):
    user_kyc, created = UserKYC.objects.get_or_create(user=request.user)
    return render(request, 'accounts/kyc_status.html', {'kyc': user_kyc})


@login_required
def age_verification(request):
    user_verification, created = UserVerification.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        date_of_birth = request.POST.get('date_of_birth')
        # In a real implementation, you would verify the age here
        # For now, we'll just simulate it
        
        user_verification.age_verified = True
        user_verification.age_verified_at = timezone.now()
        user_verification.save()
        
        messages.success(request, 'Age verified successfully')
        return redirect('community:rooms')
    
    return render(request, 'accounts/age_verification.html')
