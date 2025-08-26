from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone

from .models import CartItem, Order, OrderItem, OrderStatus, Payment
from apps.products.models import Product
from apps.accounts.models import User


@login_required
def cart(request):
    # Get cart items for the current user
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    # Calculate subtotal
    subtotal = sum(item.total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'item_count': cart_items.count(),
    }
    
    return render(request, 'orders/cart.html', context)


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if item is already in cart
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already in cart
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Updated quantity of {product.name} in your cart.')
        else:
            messages.success(request, f'Added {product.name} to your cart.')
        
        return redirect('orders:cart')
    
    return redirect('products:product_list')


@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        
        return redirect('orders:cart')
    
    return redirect('orders:cart')


@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} removed from your cart.')
        return redirect('orders:cart')
    
    return redirect('orders:cart')


@login_required
def clear_cart(request):
    if request.method == 'POST':
        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, 'Cart cleared successfully.')
        return redirect('orders:cart')
    
    return redirect('orders:cart')


@login_required
def checkout(request):
    # Get cart items for the current user
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('orders:cart')
    
    # Calculate subtotal
    subtotal = sum(item.total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def process_checkout(request):
    if request.method == 'POST':
        # Get delivery address
        delivery_address = request.POST.get('delivery_address')
        
        if not delivery_address:
            messages.error(request, 'Please provide a delivery address.')
            return redirect('orders:checkout')
        
        # Get cart items
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('orders:cart')
        
        # Calculate total amount
        total_amount = sum(item.total_price() for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}",
            total_amount=total_amount,
            delivery_address=delivery_address,
            status='pending'
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.total_price()
            )
        
        # Create initial order status
        OrderStatus.objects.create(
            order=order,
            status='pending',
            notes='Order created'
        )
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f'Order #{order.order_number} created successfully!')
        return redirect('orders:order_detail', order_id=order.id)
    
    return redirect('orders:checkout')


@login_required
def order_history(request):
    # Get user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate results
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all().select_related('product')
    order_status_history = order.status_history.all().order_by('-created_at')
    
    context = {
        'order': order,
        'order_items': order_items,
        'order_status_history': order_status_history,
    }
    
    return render(request, 'orders/order_detail.html', context)
