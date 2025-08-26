from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import CartItem, Order, OrderItem, OrderStatus, Payment
from apps.products.models import Category, Product

User = get_user_model()


class OrdersModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='testseller',
            email='seller@example.com',
            password='testpass123',
            user_type='seller'
        )
        self.category = Category.objects.create(
            name='Skincare',
            description='Skincare products'
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Test Product',
            description='This is a test product',
            price=25.99,
            quantity=10
        )
    
    def test_cart_item_creation(self):
        """Test that a cart item can be created"""
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart_item.user, self.user)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.total_price(), 51.98)
    
    def test_order_creation(self):
        """Test that an order can be created"""
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-20230101-001',
            total_amount=25.99,
            delivery_address='123 Test Street, Test City, TC 12345'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.order_number, 'ORD-20230101-001')
        self.assertEqual(order.total_amount, 25.99)
        self.assertEqual(order.status, 'pending')
    
    def test_order_item_creation(self):
        """Test that an order item can be created"""
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-20230101-001',
            total_amount=25.99,
            delivery_address='123 Test Street, Test City, TC 12345'
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            unit_price=25.99,
            total_price=25.99
        )
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.unit_price, 25.99)
    
    def test_order_status_creation(self):
        """Test that an order status can be created"""
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-20230101-001',
            total_amount=25.99,
            delivery_address='123 Test Street, Test City, TC 12345'
        )
        order_status = OrderStatus.objects.create(
            order=order,
            status='processing',
            notes='Order is being processed'
        )
        self.assertEqual(order_status.order, order)
        self.assertEqual(order_status.status, 'processing')
        self.assertEqual(order_status.notes, 'Order is being processed')
    
    def test_payment_creation(self):
        """Test that a payment can be created"""
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-20230101-001',
            total_amount=25.99,
            delivery_address='123 Test Street, Test City, TC 12345'
        )
        payment = Payment.objects.create(
            order=order,
            payment_method='credit_card',
            transaction_id='txn_123456789',
            amount=25.99,
            status='completed'
        )
        self.assertEqual(payment.order, order)
        self.assertEqual(payment.payment_method, 'credit_card')
        self.assertEqual(payment.transaction_id, 'txn_123456789')
        self.assertEqual(payment.amount, 25.99)
        self.assertEqual(payment.status, 'completed')


class OrdersViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='testseller',
            email='seller@example.com',
            password='testpass123',
            user_type='seller'
        )
        self.category = Category.objects.create(
            name='Skincare',
            description='Skincare products'
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Test Product',
            description='This is a test product',
            price=25.99,
            quantity=10
        )
    
    def test_cart_view_authenticated(self):
        """Test that the cart view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('orders:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shopping Cart')
    
    def test_add_to_cart_view_authenticated_post(self):
        """Test that an authenticated user can add items to cart"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('orders:add_to_cart'), {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful addition
        self.assertTrue(CartItem.objects.filter(user=self.user, product=self.product).exists())
    
    def test_update_cart_item_view_authenticated_post(self):
        """Test that an authenticated user can update cart items"""
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('orders:update_cart_item', args=[cart_item.id]), {
            'quantity': 3
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)
    
    def test_remove_from_cart_view_authenticated_post(self):
        """Test that an authenticated user can remove items from cart"""
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('orders:remove_from_cart', args=[cart_item.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful removal
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_checkout_view_authenticated_with_items(self):
        """Test that the checkout view works for authenticated users with items in cart"""
        CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Checkout')
    
    def test_process_checkout_view_authenticated_post(self):
        """Test that an authenticated user can process checkout"""
        CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('orders:process_checkout'), {
            'delivery_address': '123 Test Street, Test City, TC 12345'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful checkout
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())  # Cart should be cleared
    
    def test_order_history_view_authenticated(self):
        """Test that the order history view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order History')
    
    def test_order_detail_view_authenticated_owner(self):
        """Test that the order detail view works for authenticated owners"""
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-20230101-001',
            total_amount=25.99,
            delivery_address='123 Test Street, Test City, TC 12345'
        )
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('orders:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order Details')
