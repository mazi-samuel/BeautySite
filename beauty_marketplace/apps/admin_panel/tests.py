from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import AdminAction, Report, SystemSetting
from apps.community.models import CommunityPost, CommunityMessage

User = get_user_model()


class AdminPanelModelTests(TestCase):
    def setUp(self):
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
    
    def test_admin_action_creation(self):
        """Test that an admin action can be created"""
        action = AdminAction.objects.create(
            admin_user=self.admin_user,
            action_type='user_activation',
            description='Activated user account',
            affected_user=self.user
        )
        self.assertEqual(action.admin_user, self.admin_user)
        self.assertEqual(action.action_type, 'user_activation')
        self.assertEqual(action.description, 'Activated user account')
        self.assertEqual(action.affected_user, self.user)
    
    def test_report_creation(self):
        """Test that a report can be created"""
        report = Report.objects.create(
            reported_by=self.user,
            report_type='post',
            content_id=1,
            report_reason='spam',
            description='This post is spam'
        )
        self.assertEqual(report.reported_by, self.user)
        self.assertEqual(report.report_type, 'post')
        self.assertEqual(report.report_reason, 'spam')
        self.assertEqual(report.description, 'This post is spam')
        self.assertFalse(report.is_resolved)
    
    def test_system_setting_creation(self):
        """Test that a system setting can be created"""
        setting = SystemSetting.objects.create(
            key='site_name',
            value='BeautyMarket',
            description='Name of the website'
        )
        self.assertEqual(setting.key, 'site_name')
        self.assertEqual(setting.value, 'BeautyMarket')
        self.assertEqual(setting.description, 'Name of the website')
        self.assertTrue(setting.is_active)


class AdminPanelViewTests(TestCase):
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
    
    def test_admin_dashboard_view_unauthenticated(self):
        """Test that the admin dashboard view redirects unauthenticated users"""
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to admin login
    
    def test_admin_dashboard_view_authenticated_non_staff(self):
        """Test that the admin dashboard view redirects non-staff users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to admin login
    
    def test_admin_dashboard_view_authenticated_staff(self):
        """Test that the admin dashboard view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
    
    def test_user_management_view_authenticated_staff(self):
        """Test that the user management view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Management')
    
    def test_product_approval_view_authenticated_staff(self):
        """Test that the product approval view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:product_approval'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product Approval')
    
    def test_kyc_review_view_authenticated_staff(self):
        """Test that the KYC review view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:kyc_review'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'KYC Review')
    
    def test_community_moderation_view_authenticated_staff(self):
        """Test that the community moderation view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:community_moderation'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Community Moderation')
    
    def test_ad_management_view_authenticated_staff(self):
        """Test that the ad management view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:ad_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Advertisement Management')
    
    def test_analytics_dashboard_view_authenticated_staff(self):
        """Test that the analytics dashboard view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('admin_panel:analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics Dashboard')


class AdminPanelActionTests(TestCase):
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
    
    def test_user_activation_action(self):
        """Test that an admin can activate a user"""
        self.user.is_active = False
        self.user.save()
        
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.post(reverse('admin_panel:user_activation', args=[self.user.id]), {
            'action': 'activate'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful action
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        
        # Check that admin action was recorded
        self.assertTrue(AdminAction.objects.filter(
            admin_user=self.admin_user,
            action_type='user_activation',
            affected_user=self.user
        ).exists())
    
    def test_user_suspension_action(self):
        """Test that an admin can suspend a user"""
        self.user.is_active = True
        self.user.save()
        
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.post(reverse('admin_panel:user_activation', args=[self.user.id]), {
            'action': 'suspend'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful action
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        # Check that admin action was recorded
        self.assertTrue(AdminAction.objects.filter(
            admin_user=self.admin_user,
            action_type='user_suspension',
            affected_user=self.user
        ).exists())
    
    def test_content_removal_action(self):
        """Test that an admin can remove inappropriate content"""
        post = CommunityPost.objects.create(
            room_id=1,  # We'll use a dummy room ID for testing
            user=self.user,
            title='Inappropriate Post',
            content='This is inappropriate content'
        )
        
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.post(reverse('admin_panel:remove_content'), {
            'content_type': 'post',
            'content_id': post.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful action
        
        # Check that admin action was recorded
        self.assertTrue(AdminAction.objects.filter(
            admin_user=self.admin_user,
            action_type='content_removal',
            affected_post=post
        ).exists())
    
    def test_report_resolution_action(self):
        """Test that an admin can resolve a report"""
        report = Report.objects.create(
            reported_by=self.user,
            report_type='post',
            content_id=1,
            report_reason='spam',
            description='This post is spam'
        )
        
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.post(reverse('admin_panel:resolve_report', args=[report.id]), {
            'resolution': 'removed'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful action
        report.refresh_from_db()
        self.assertTrue(report.is_resolved)
        self.assertEqual(report.resolved_by, self.admin_user)
