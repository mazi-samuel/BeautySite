from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import CommunityRoom, CommunityPost, CommunityMessage
from apps.accounts.models import User, UserVerification


def community_home(request):
    # Get public rooms
    public_rooms = CommunityRoom.objects.filter(is_private=False).order_by('-created_at')
    
    # Get user's private rooms if logged in
    user_rooms = []
    if request.user.is_authenticated:
        user_rooms = CommunityRoom.objects.filter(
            Q(created_by=request.user) | Q(is_private=True)
        ).order_by('-created_at')
    
    context = {
        'public_rooms': public_rooms,
        'user_rooms': user_rooms,
    }
    
    return render(request, 'community/home.html', context)


@login_required
def rooms(request):
    # Check if user has verified their age for adult content
    user_verification, created = UserVerification.objects.get_or_create(user=request.user)
    
    # Get filter parameters
    search = request.GET.get('search', '')
    adult_content = request.GET.get('adult_content', '')
    
    # Build queryset
    rooms = CommunityRoom.objects.all().order_by('-created_at')
    
    if search:
        rooms = rooms.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Filter for adult content if user has verified age
    if adult_content and user_verification.age_verified:
        rooms = rooms.filter(is_adult_content=True)
    else:
        rooms = rooms.filter(is_adult_content=False)
    
    # Paginate results
    paginator = Paginator(rooms, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search,
        'adult_content_filter': adult_content,
        'age_verified': user_verification.age_verified,
    }
    
    return render(request, 'community/rooms.html', context)


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(CommunityRoom, id=room_id)
    
    # Check if user can access this room
    if room.is_private and request.user != room.created_by:
        messages.error(request, 'You do not have access to this private room.')
        return redirect('community:rooms')
    
    # Check age verification for adult content
    if room.is_adult_content:
        user_verification, created = UserVerification.objects.get_or_create(user=request.user)
        if not user_verification.age_verified:
            messages.warning(request, 'You need to verify your age to access adult content.')
            return redirect('accounts:age_verification')
    
    # Get posts in this room
    posts = CommunityPost.objects.filter(room=room).order_by('-created_at')
    
    # Paginate results
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'room': room,
        'page_obj': page_obj,
    }
    
    return render(request, 'community/room_detail.html', context)


@login_required
def create_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_private = request.POST.get('is_private') == 'on'
        is_adult_content = request.POST.get('is_adult_content') == 'on'
        
        # Check age verification for adult content
        if is_adult_content:
            user_verification, created = UserVerification.objects.get_or_create(user=request.user)
            if not user_verification.age_verified:
                messages.error(request, 'You need to verify your age to create adult content rooms.')
                return redirect('accounts:age_verification')
        
        # Create room
        room = CommunityRoom.objects.create(
            name=name,
            description=description,
            is_private=is_private,
            is_adult_content=is_adult_content,
            created_by=request.user
        )
        
        messages.success(request, f'Room "{room.name}" created successfully!')
        return redirect('community:room_detail', room_id=room.id)
    
    return render(request, 'community/create_room.html')


@login_required
def create_post(request, room_id):
    room = get_object_or_404(CommunityRoom, id=room_id)
    
    # Check if user can access this room
    if room.is_private and request.user != room.created_by:
        messages.error(request, 'You do not have access to this private room.')
        return redirect('community:rooms')
    
    # Check age verification for adult content
    if room.is_adult_content:
        user_verification, created = UserVerification.objects.get_or_create(user=request.user)
        if not user_verification.age_verified:
            messages.warning(request, 'You need to verify your age to post in adult content rooms.')
            return redirect('accounts:age_verification')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        # Create post
        post = CommunityPost.objects.create(
            room=room,
            user=request.user,
            title=title,
            content=content
        )
        
        messages.success(request, 'Post created successfully!')
        return redirect('community:room_detail', room_id=room.id)
    
    context = {
        'room': room,
    }
    
    return render(request, 'community/create_post.html', context)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    
    # Check if user can access this post's room
    room = post.room
    if room.is_private and request.user != room.created_by:
        messages.error(request, 'You do not have access to this private room.')
        return redirect('community:rooms')
    
    # Check age verification for adult content
    if room.is_adult_content:
        user_verification, created = UserVerification.objects.get_or_create(user=request.user)
        if not user_verification.age_verified:
            messages.warning(request, 'You need to verify your age to view this content.')
            return redirect('accounts:age_verification')
    
    # Get messages for this post
    messages_list = CommunityMessage.objects.filter(post=post).order_by('created_at')
    
    context = {
        'post': post,
        'messages': messages_list,
        'room': room,
    }
    
    return render(request, 'community/post_detail.html', context)


@login_required
def add_message(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    
    # Check if user can access this post's room
    room = post.room
    if room.is_private and request.user != room.created_by:
        messages.error(request, 'You do not have access to this private room.')
        return redirect('community:rooms')
    
    # Check age verification for adult content
    if room.is_adult_content:
        user_verification, created = UserVerification.objects.get_or_create(user=request.user)
        if not user_verification.age_verified:
            messages.warning(request, 'You need to verify your age to participate in this discussion.')
            return redirect('accounts:age_verification')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        # Create message
        CommunityMessage.objects.create(
            post=post,
            user=request.user,
            content=content
        )
        
        messages.success(request, 'Message added successfully!')
        return redirect('community:post_detail', post_id=post.id)
    
    return redirect('community:post_detail', post_id=post.id)


@login_required
def private_messages(request):
    # Get users the current user has messaged or been messaged by
    # This is a simplified implementation - in a real app you would have a more complex system
    message_partners = User.objects.filter(
        Q(communitymessage__user=request.user) | Q(communitypost__user=request.user)
    ).distinct().exclude(id=request.user.id)
    
    context = {
        'message_partners': message_partners,
    }
    
    return render(request, 'community/private_messages.html', context)


@login_required
def private_message_thread(request, user_id):
    partner = get_object_or_404(User, id=user_id)
    
    # Get messages between current user and partner
    # This is a simplified implementation - in a real app you would have a more complex system
    messages_list = CommunityMessage.objects.filter(
        Q(user=request.user, post__user=partner) | Q(user=partner, post__user=request.user)
    ).order_by('created_at')
    
    context = {
        'partner': partner,
        'messages': messages_list,
    }
    
    return render(request, 'community/private_message_thread.html', context)
