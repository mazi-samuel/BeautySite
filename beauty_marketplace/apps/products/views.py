from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Product, Category, ProductReview
from apps.accounts.models import User


def home(request):
    # Get featured products (for now, we'll just get the latest 6)
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
    
    # Get categories
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    
    return render(request, 'products/home.html', context)


def product_list(request):
    # Get filter parameters
    category_id = request.GET.get('category', '')
    search = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', 'newest')
    
    # Build queryset
    products = Product.objects.filter(is_active=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Apply sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rating':
        # In a real implementation, you would order by rating
        products = products.order_by('-created_at')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Paginate results
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_id,
        'search_query': search,
        'min_price_filter': min_price,
        'max_price_filter': max_price,
        'sort_filter': sort,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get related products (same category, excluding current product)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product_id).order_by('-created_at')[:4]
    
    # Get reviews
    reviews = product.reviews.all().order_by('-created_at')
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    }
    
    return render(request, 'products/product_detail.html', context)


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Check if user has already reviewed this product
        review, created = ProductReview.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        
        if not created:
            # Update existing review
            review.rating = rating
            review.comment = comment
            review.save()
            messages.success(request, 'Your review has been updated.')
        else:
            messages.success(request, 'Your review has been added.')
        
        return redirect('products:product_detail', product_id=product_id)
    
    return redirect('products:product_detail', product_id=product_id)


@login_required
def seller_dashboard(request):
    if request.user.user_type != 'seller':
        messages.error(request, 'You must be a seller to access this page.')
        return redirect('products:home')
    
    # Get seller's products
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    context = {
        'products': products,
    }
    
    return render(request, 'products/seller_dashboard.html', context)


@login_required
def create_product(request):
    if request.user.user_type != 'seller':
        messages.error(request, 'You must be a seller to access this page.')
        return redirect('products:home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        category_id = request.POST.get('category')
        
        # Create product
        product = Product.objects.create(
            seller=request.user,
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            category_id=category_id,
            is_active=False  # Product needs admin approval
        )
        
        # Handle image uploads (simplified for now)
        # In a real implementation, you would handle file uploads properly
        image_urls = request.POST.getlist('image_urls')
        for i, image_url in enumerate(image_urls):
            if image_url:
                from .models import ProductImage
                ProductImage.objects.create(
                    product=product,
                    image_url=image_url,
                    is_primary=(i == 0),
                    sort_order=i
                )
        
        messages.success(request, 'Product created successfully and is pending approval.')
        return redirect('products:seller_dashboard')
    
    # Get categories for form
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'products/create_product.html', context)


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.category_id = request.POST.get('category')
        product.save()
        
        # Handle image updates (simplified for now)
        # In a real implementation, you would handle file uploads properly
        image_urls = request.POST.getlist('image_urls')
        # Clear existing images
        product.images.all().delete()
        # Add new images
        for i, image_url in enumerate(image_urls):
            if image_url:
                from .models import ProductImage
                ProductImage.objects.create(
                    product=product,
                    image_url=image_url,
                    is_primary=(i == 0),
                    sort_order=i
                )
        
        messages.success(request, 'Product updated successfully.')
        return redirect('products:seller_dashboard')
    
    # Get categories for form
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'product': product,
        'categories': categories,
    }
    
    return render(request, 'products/edit_product.html', context)


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('products:seller_dashboard')
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/delete_product.html', context)
