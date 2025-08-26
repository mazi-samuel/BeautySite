from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import UserActivity, ProductView, SearchQuery, RevenueReport, UserSignup

User = get_user_model()


class AnalyticsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_activity_creation(self):
        """Test that a user activity can be created"""
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='login',
            description='User logged in',
            ip_address='127.0.0.1'
        )
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'login')
        self.assertEqual(activity.description, 'User logged in')
        self.assertEqual(activity.ip_address, '127.0.0.1')
    
    def test_product_view_creation(self):
        """Test that a product view can be created"""
        view = ProductView.objects.create(
            product_id=1,  # We'll use a dummy product ID for testing
            user=self.user,
            ip_address='127.0.0.1'
        )
        self.assertEqual(view.product_id, 1)
        self.assertEqual(view.user, self.user)
        self.assertEqual(view.ip_address, '127.0.0.1')
    
    def test_search_query_creation(self):
        """Test that a search query can be created"""
        query = SearchQuery.objects.create(
            user=self.user,
            query='skincare',
            result_count=10,
            ip_address='127.0.0.1'
        )
        self.assertEqual(query.user, self.user)
        self.assertEqual(query.query, 'skincare')
        self.assertEqual(query.result_count, 10)
        self.assertEqual(query.ip_address, '127.0.0.1')
    
    def test_revenue_report_creation(self):
        """Test that a revenue report can be created"""
        report = RevenueReport.objects.create(
            date=timezone.now().date(),
            total_revenue=1000.00,
            order_count=25,
            product_count=50
        )
        self.assertEqual(report.date, timezone.now().date())
        self.assertEqual(report.total_revenue, 1000.00)
        self.assertEqual(report.order_count, 25)
        self.assertEqual(report.product_count, 50)
    
    def test_user_signup_creation(self):
        """Test that a user signup can be created"""
        signup = UserSignup.objects.create(
            date=timezone.now().date(),
            signup_count=10
        )
        self.assertEqual(signup.date, timezone.now().date())
        self.assertEqual(signup.signup_count, 10)


class AnalyticsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_analytics_dashboard_view_unauthenticated(self):
        """Test that the analytics dashboard view redirects unauthenticated users"""
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_analytics_dashboard_view_authenticated_non_staff(self):
        """Test that the analytics dashboard view redirects non-staff users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to admin login
    
    def test_analytics_dashboard_view_authenticated_staff(self):
        """Test that the analytics dashboard view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics Dashboard')
    
    def test_user_activity_report_view_authenticated_staff(self):
        """Test that the user activity report view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('analytics:user_activity'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Activity Report')
    
    def test_product_performance_report_view_authenticated_staff(self):
        """Test that the product performance report view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('analytics:product_performance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product Performance Report')
    
    def test_search_analytics_report_view_authenticated_staff(self):
        """Test that the search analytics report view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('analytics:search_analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Analytics Report')
    
    def test_revenue_report_view_authenticated_staff(self):
        """Test that the revenue report view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('analytics:revenue'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Revenue Report')
    
    def test_user_signup_report_view_authenticated_staff(self):
        """Test that the user signup report view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('analytics:user_signups'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Signup Report')


class AnalyticsDataCollectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login_activity_tracked(self):
        """Test that user login activity is tracked"""
        # Login the user
        self.client.login(email='test@example.com', password='testpass123')
        
        # Check that login activity was recorded
        self.assertTrue(UserActivity.objects.filter(
            user=self.user,
            activity_type='login'
        ).exists())
    
    def test_product_view_tracked(self):
        """Test that product views are tracked"""
        self.client.login(email='test@example.com', password='testpass123')
        
        # Simulate viewing a product (we'll use a dummy product ID)
        response = self.client.get('/products/1/')  # This will be a 404 but that's okay for testing
        
        # Check that product view was recorded
        self.assertTrue(ProductView.objects.filter(
            user=self.user,
            product_id=1
        ).exists())
    
    def test_search_query_tracked(self):
        """Test that search queries are tracked"""
        self.client.login(email='test@example.com', password='testpass123')
        
        # Simulate a search
        response = self.client.get('/search/?q=skincare')
        
        # Check that search query was recorded
        self.assertTrue(SearchQuery.objects.filter(
            user=self.user,
            query='skincare'
        ).exists())
    
    def test_revenue_report_generation(self):
        """Test that revenue reports can be generated"""
        # Create a revenue report
        report = RevenueReport.objects.create(
            date=timezone.now().date(),
            total_revenue=1500.00,
            order_count=30,
            product_count=60
        )
        
        # Check that the report was created
        self.assertTrue(RevenueReport.objects.filter(
            date=timezone.now().date()
        ).exists())
        
        # Check that the report has the correct data
        report.refresh_from_db()
        self.assertEqual(report.total_revenue, 1500.00)
        self.assertEqual(report.order_count, 30)
        self.assertEqual(report.product_count, 60)
    
    def test_user_signup_tracked(self):
        """Test that user signups are tracked"""
        # Create a new user (this should trigger signup tracking)
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpass123'
        )
        
        # Check that user signup was recorded
        self.assertTrue(UserSignup.objects.filter(
            date=timezone.now().date()
        ).exists())
        
        # Check that the signup count was incremented
        signup = UserSignup.objects.get(date=timezone.now().date())
        self.assertGreater(signup.signup_count, 0)
