from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import Category, Product, ProductImage, ProductReview

User = get_user_model()


class ProductsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='seller'
        )
        self.category = Category.objects.create(
            name='Skincare',
            description='Skincare products'
        )
    
    def test_category_creation(self):
        """Test that a category can be created"""
        self.assertEqual(self.category.name, 'Skincare')
        self.assertEqual(self.category.description, 'Skincare products')
        self.assertTrue(self.category.is_active)
    
    def test_product_creation(self):
        """Test that a product can be created"""
        product = Product.objects.create(
            seller=self.user,
            category=self.category,
            name='Test Product',
            description='This is a test product',
            price=25.99,
            quantity=10
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 25.99)
        self.assertEqual(product.quantity, 10)
        self.assertTrue(product.is_active)
    
    def test_product_image_creation(self):
        """Test that a product image can be created"""
        product = Product.objects.create(
            seller=self.user,
            category=self.category,
            name='Test Product',
            description='This is a test product',
            price=25.99,
            quantity=10
        )
        image = ProductImage.objects.create(
            product=product,
            image_url='https://example.com/image.jpg',
            is_primary=True
        )
        self.assertEqual(image.product, product)
        self.assertEqual(image.image_url, 'https://example.com/image.jpg')
        self.assertTrue(image.is_primary)
    
    def test_product_review_creation(self):
        """Test that a product review can be created"""
        product = Product.objects.create(
            seller=self.user,
            category=self.category,
            name='Test Product',
            description='This is a test product',
            price=25.99,
            quantity=10
        )
        review = ProductReview.objects.create(
            product=product,
            user=self.user,
            rating=5,
            comment='This is an excellent product!'
        )
        self.assertEqual(review.product, product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'This is an excellent product!')


class ProductsViewTests(TestCase):
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
    
    def test_product_list_view(self):
        """Test that the product list view returns a 200 response"""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_product_detail_view(self):
        """Test that the product detail view returns a 200 response"""
        response = self.client.get(reverse('products:product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_seller_dashboard_view_authenticated_seller(self):
        """Test that the seller dashboard view works for authenticated sellers"""
        self.client.login(email='seller@example.com', password='testpass123')
        response = self.client.get(reverse('products:seller_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seller Dashboard')
    
    def test_seller_dashboard_view_authenticated_buyer(self):
        """Test that the seller dashboard view redirects for authenticated buyers"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('products:seller_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to home
    
    def test_create_product_view_authenticated_seller_get(self):
        """Test that the create product view returns a 200 response for sellers"""
        self.client.login(email='seller@example.com', password='testpass123')
        response = self.client.get(reverse('products:create_product'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New Product')
    
    def test_create_product_view_authenticated_seller_post(self):
        """Test that a seller can create a product"""
        self.client.login(email='seller@example.com', password='testpass123')
        response = self.client.post(reverse('products:create_product'), {
            'name': 'New Test Product',
            'category': self.category.id,
            'price': 35.99,
            'quantity': 5,
            'description': 'This is a new test product'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Product.objects.filter(name='New Test Product').exists())
    
    def test_edit_product_view_authenticated_seller_get(self):
        """Test that the edit product view returns a 200 response for sellers"""
        self.client.login(email='seller@example.com', password='testpass123')
        response = self.client.get(reverse('products:edit_product', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Product')
    
    def test_edit_product_view_authenticated_seller_post(self):
        """Test that a seller can edit a product"""
        self.client.login(email='seller@example.com', password='testpass123')
        response = self.client.post(reverse('products:edit_product', args=[self.product.id]), {
            'name': 'Updated Test Product',
            'category': self.category.id,
            'price': 45.99,
            'quantity': 3,
            'description': 'This is an updated test product'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Test Product')
        self.assertEqual(self.product.price, 45.99)
    
    def test_delete_product_view_authenticated_seller_post(self):
        """Test that a seller can delete a product"""
        self.client.login(email='seller@example.com', password='testpass123')
        response = self.client.post(reverse('products:delete_product', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
