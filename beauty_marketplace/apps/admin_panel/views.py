from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

from apps.accounts.models import User, UserKYC
from apps.products.models import Product
from apps.community.models import CommunityPost, CommunityMessage
from apps.advertisements.models import Advertisement
from apps.orders.models import Order
from apps.analytics.models import RevenueReport, UserSignup

from .models import Report, AdminAction


def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'


@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = sum(order.total_amount for order in Order.objects.all())
    
    # Get recent reports
    recent_reports = Report.objects.filter(is_resolved=False).order_by('-created_at')[:5]
    
    # Get recent user signups
    recent_signups = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_reports': recent_reports,
        'recent_signups': recent_signups,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@user_passes_test(is_admin)
def user_management(request):
    # Get filter parameters
    user_type = request.GET.get('user_type', '')
    is_active = request.GET.get('is_active', '')
    kyc_status = request.GET.get('kyc_status', '')
    search = request.GET.get('search', '')
    
    # Build queryset
    users = User.objects.all().order_by('-date_joined')
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    if is_active:
        is_active_bool = is_active.lower() == 'true'
        users = users.filter(is_active=is_active_bool)
    
    if kyc_status:
        users = users.filter(kyc__status=kyc_status)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Paginate results
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_type_filter': user_type,
        'is_active_filter': is_active,
        'kyc_status_filter': kyc_status,
        'search_query': search,
    }
    
    return render(request, 'admin_panel/user_management.html', context)


@user_passes_test(is_admin)
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    kyc = getattr(user, 'kyc', None)
    
    context = {
        'user': user,
        'kyc': kyc,
    }
    
    return render(request, 'admin_panel/user_detail.html', context)


@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Toggle user status
    user.is_active = not user.is_active
    user.save()
    
    # Log admin action
    AdminAction.objects.create(
        admin_user=request.user,
        action_type='user_activation' if user.is_active else 'user_suspension',
        description=f"{'Activated' if user.is_active else 'Suspended'} user {user.username}",
        affected_user=user
    )
    
    messages.success(request, f"User {user.username} has been {'activated' if user.is_active else 'suspended'}.")
    return redirect('admin_panel:user_management')


@user_passes_test(is_admin)
def kyc_review(request):
    # Get filter parameters
    status = request.GET.get('status', 'pending')
    search = request.GET.get('search', '')
    
    # Build queryset
    kyc_submissions = UserKYC.objects.filter(status=status).order_by('-submitted_at')
    
    if search:
        kyc_submissions = kyc_submissions.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Paginate results
    paginator = Paginator(kyc_submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'search_query': search,
    }
    
    return render(request, 'admin_panel/kyc_review.html', context)


@user_passes_test(is_admin)
def kyc_review_detail(request, kyc_id):
    kyc = get_object_or_404(UserKYC, id=kyc_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if action == 'approve':
            kyc.status = 'verified'
            kyc.reviewed_at = timezone.now()
            kyc.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='kyc_approval',
                description=f"Approved KYC for user {kyc.user.username}",
                affected_user=kyc.user
            )
            
            messages.success(request, f"KYC for {kyc.user.username} has been approved.")
        elif action == 'reject':
            kyc.status = 'rejected'
            kyc.rejection_reason = rejection_reason
            kyc.reviewed_at = timezone.now()
            kyc.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='kyc_rejection',
                description=f"Rejected KYC for user {kyc.user.username}: {rejection_reason}",
                affected_user=kyc.user
            )
            
            messages.success(request, f"KYC for {kyc.user.username} has been rejected.")
        
        return redirect('admin_panel:kyc_review')
    
    context = {
        'kyc': kyc,
    }
    
    return render(request, 'admin_panel/kyc_review_detail.html', context)


@user_passes_test(is_admin)
def product_approval(request):
    # Get filter parameters
    status = request.GET.get('status', 'pending')
    search = request.GET.get('search', '')
    
    # For now, we'll assume all products need approval
    # In a real implementation, you might have a status field on Product model
    products = Product.objects.all().order_by('-created_at')
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(seller__username__icontains=search)
        )
    
    # Paginate results
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'search_query': search,
    }
    
    return render(request, 'admin_panel/product_approval.html', context)


@user_passes_test(is_admin)
def product_review_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if action == 'approve':
            product.is_active = True
            product.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='product_approval',
                description=f"Approved product {product.name}",
                affected_user=product.seller
            )
            
            messages.success(request, f"Product '{product.name}' has been approved.")
        elif action == 'reject':
            product.is_active = False
            product.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='product_rejection',
                description=f"Rejected product {product.name}: {rejection_reason}",
                affected_user=product.seller
            )
            
            messages.success(request, f"Product '{product.name}' has been rejected.")
        
        return redirect('admin_panel:product_approval')
    
    context = {
        'product': product,
    }
    
    return render(request, 'admin_panel/product_review_detail.html', context)


@user_passes_test(is_admin)
def community_moderation(request):
    # Get filter parameters
    search = request.GET.get('search', '')
    
    # Get reported content
    reports = Report.objects.filter(is_resolved=False).order_by('-created_at')
    
    if search:
        reports = reports.filter(
            Q(description__icontains=search) |
            Q(reported_by__username__icontains=search)
        )
    
    # Paginate results
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search,
    }
    
    return render(request, 'admin_panel/community_moderation.html', context)


@user_passes_test(is_admin)
def handle_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'remove':
            # Remove the reported content
            if report.report_type == 'post':
                post = get_object_or_404(CommunityPost, id=report.content_id)
                post.delete()
            elif report.report_type == 'message':
                message = get_object_or_404(CommunityMessage, id=report.content_id)
                message.delete()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='content_removal',
                description=f"Removed {report.report_type} reported by {report.reported_by.username}",
                affected_post=getattr(post, 'id', None) if report.report_type == 'post' else None,
                affected_message=getattr(message, 'id', None) if report.report_type == 'message' else None
            )
            
            messages.success(request, f"The {report.report_type} has been removed.")
        elif action == 'warn':
            # In a real implementation, you might send a warning to the user
            messages.success(request, f"A warning has been sent to the user.")
        elif action == 'ban':
            # Ban the user
            user_to_ban = None
            if report.report_type == 'post':
                post = get_object_or_404(CommunityPost, id=report.content_id)
                user_to_ban = post.user
            elif report.report_type == 'message':
                message = get_object_or_404(CommunityMessage, id=report.content_id)
                user_to_ban = message.user
            
            if user_to_ban:
                user_to_ban.is_active = False
                user_to_ban.save()
                
                # Log admin action
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='user_ban',
                    description=f"Banned user {user_to_ban.username}",
                    affected_user=user_to_ban
                )
                
                messages.success(request, f"User {user_to_ban.username} has been banned.")
        
        # Mark report as resolved
        report.is_resolved = True
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.save()
        
        return redirect('admin_panel:community_moderation')
    
    context = {
        'report': report,
    }
    
    return render(request, 'admin_panel/handle_report.html', context)


@user_passes_test(is_admin)
def advertisement_management(request):
    # Get filter parameters
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Build queryset
    ads = Advertisement.objects.all().order_by('-created_at')
    
    if status:
        ads = ads.filter(status=status)
    
    if search:
        ads = ads.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Paginate results
    paginator = Paginator(ads, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'search_query': search,
    }
    
    return render(request, 'admin_panel/advertisement_management.html', context)


@user_passes_test(is_admin)
def advertisement_detail(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            ad.status = 'active'
            ad.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='ad_approval',
                description=f"Approved advertisement {ad.title}"
            )
            
            messages.success(request, f"Advertisement '{ad.title}' has been approved.")
        elif action == 'reject':
            ad.status = 'draft'
            ad.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='ad_rejection',
                description=f"Rejected advertisement {ad.title}"
            )
            
            messages.success(request, f"Advertisement '{ad.title}' has been rejected.")
        
        return redirect('admin_panel:advertisement_management')
    
    context = {
        'ad': ad,
    }
    
    return render(request, 'admin_panel/advertisement_detail.html', context)


@user_passes_test(is_admin)
def analytics_dashboard(request):
    # Get filter parameters
    period = request.GET.get('period', 'month')
    
    # Get analytics data
    if period == 'day':
        revenue_data = RevenueReport.objects.order_by('-date')[:30]
        signup_data = UserSignup.objects.order_by('-date')[:30]
    elif period == 'week':
        revenue_data = RevenueReport.objects.order_by('-date')[:12]
        signup_data = UserSignup.objects.order_by('-date')[:12]
    else:  # month
        revenue_data = RevenueReport.objects.order_by('-date')[:6]
        signup_data = UserSignup.objects.order_by('-date')[:6]
    
    context = {
        'revenue_data': revenue_data,
        'signup_data': signup_data,
        'period_filter': period,
    }
    
    return render(request, 'admin_panel/analytics_dashboard.html', context)
