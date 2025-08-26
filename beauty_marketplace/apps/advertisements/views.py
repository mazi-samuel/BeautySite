from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Advertisement, AdvertisementSlot


def get_active_ads(request):
    """Get active advertisements for display"""
    ads = Advertisement.objects.filter(
        status='active',
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    return ads


def ad_slots(request):
    """Display advertisement slots"""
    # Get all advertisement slots with their active ads
    slots = AdvertisementSlot.objects.select_related('advertisement').filter(
        advertisement__status='active',
        advertisement__start_date__lte=timezone.now().date(),
        advertisement__end_date__gte=timezone.now().date()
    )
    
    context = {
        'slots': slots,
    }
    
    return render(request, 'advertisements/ad_slots.html', context)


@staff_member_required
def advertisement_management(request):
    """Admin view for managing advertisements"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Build queryset
    ads = Advertisement.objects.all().order_by('-created_at')
    
    if status_filter:
        ads = ads.filter(status=status_filter)
    
    if search:
        ads = ads.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Paginate results
    paginator = Paginator(ads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search,
    }
    
    return render(request, 'advertisements/advertisement_management.html', context)


@staff_member_required
def advertisement_detail(request, ad_id):
    """Admin view for advertisement details"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            ad.status = 'active'
            ad.save()
            messages.success(request, f'Advertisement "{ad.title}" approved and activated.')
        elif action == 'reject':
            ad.status = 'draft'
            ad.save()
            messages.success(request, f'Advertisement "{ad.title}" rejected.')
        
        return redirect('advertisements:advertisement_management')
    
    context = {
        'ad': ad,
    }
    
    return render(request, 'advertisements/advertisement_detail.html', context)


@staff_member_required
def create_advertisement(request):
    """Admin view for creating advertisements"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        target_url = request.POST.get('target_url')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        budget = request.POST.get('budget', 0)
        
        # Create advertisement
        ad = Advertisement.objects.create(
            title=title,
            description=description,
            image_url=image_url,
            target_url=target_url,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            created_by=request.user
        )
        
        messages.success(request, f'Advertisement "{ad.title}" created successfully.')
        return redirect('advertisements:advertisement_management')
    
    return render(request, 'advertisements/create_advertisement.html')


@staff_member_required
def edit_advertisement(request, ad_id):
    """Admin view for editing advertisements"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if request.method == 'POST':
        ad.title = request.POST.get('title')
        ad.description = request.POST.get('description')
        ad.image_url = request.POST.get('image_url')
        ad.target_url = request.POST.get('target_url')
        ad.start_date = request.POST.get('start_date')
        ad.end_date = request.POST.get('end_date')
        ad.budget = request.POST.get('budget', 0)
        ad.save()
        
        messages.success(request, f'Advertisement "{ad.title}" updated successfully.')
        return redirect('advertisements:advertisement_detail', ad_id=ad.id)
    
    context = {
        'ad': ad,
    }
    
    return render(request, 'advertisements/edit_advertisement.html', context)


@staff_member_required
def delete_advertisement(request, ad_id):
    """Admin view for deleting advertisements"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if request.method == 'POST':
        ad_title = ad.title
        ad.delete()
        messages.success(request, f'Advertisement "{ad_title}" deleted successfully.')
        return redirect('advertisements:advertisement_management')
    
    context = {
        'ad': ad,
    }
    
    return render(request, 'advertisements/delete_advertisement.html', context)
