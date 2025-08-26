from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import Advertisement, AdvertisementSlot

User = get_user_model()


class AdvertisementsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_advertisement_creation(self):
        """Test that an advertisement can be created"""
        ad = Advertisement.objects.create(
            title='Test Ad',
            description='This is a test advertisement',
            image_url='https://example.com/ad.jpg',
            target_url='https://example.com',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            budget=100.00,
            created_by=self.user
        )
        self.assertEqual(ad.title, 'Test Ad')
        self.assertEqual(ad.description, 'This is a test advertisement')
        self.assertEqual(ad.status, 'draft')
        self.assertEqual(ad.created_by, self.user)
    
    def test_advertisement_slot_creation(self):
        """Test that an advertisement slot can be created"""
        ad = Advertisement.objects.create(
            title='Test Ad',
            description='This is a test advertisement',
            image_url='https://example.com/ad.jpg',
            target_url='https://example.com',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            budget=100.00,
            created_by=self.user
        )
        slot = AdvertisementSlot.objects.create(
            advertisement=ad,
            slot_name='Homepage Banner',
            page_location='homepage',
            dimensions='728x90'
        )
        self.assertEqual(slot.advertisement, ad)
        self.assertEqual(slot.slot_name, 'Homepage Banner')
        self.assertEqual(slot.page_location, 'homepage')
        self.assertEqual(slot.dimensions, '728x90')


class AdvertisementsViewTests(TestCase):
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
        self.ad = Advertisement.objects.create(
            title='Test Ad',
            description='This is a test advertisement',
            image_url='https://example.com/ad.jpg',
            target_url='https://example.com',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            budget=100.00,
            created_by=self.user
        )
    
    def test_ad_slots_view(self):
        """Test that the ad slots view returns a 200 response"""
        response = self.client.get(reverse('advertisements:ad_slots'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Advertisement Slots')
    
    def test_advertisement_management_view_unauthenticated(self):
        """Test that the advertisement management view redirects unauthenticated users"""
        response = self.client.get(reverse('advertisements:advertisement_management'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_advertisement_management_view_authenticated_non_staff(self):
        """Test that the advertisement management view redirects non-staff users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('advertisements:advertisement_management'))
        self.assertEqual(response.status_code, 302)  # Redirect to admin login
    
    def test_advertisement_management_view_authenticated_staff(self):
        """Test that the advertisement management view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('advertisements:advertisement_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Advertisement Management')
    
    def test_create_advertisement_view_get_authenticated_staff(self):
        """Test that the create advertisement view returns a 200 response for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('advertisements:create_advertisement'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Advertisement')
    
    def test_create_advertisement_view_post_authenticated_staff(self):
        """Test that a staff user can create an advertisement"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.post(reverse('advertisements:create_advertisement'), {
            'title': 'New Test Ad',
            'description': 'This is a new test advertisement',
            'image_url': 'https://example.com/new-ad.jpg',
            'target_url': 'https://example.com/new',
            'start_date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (timezone.now().date() + timezone.timedelta(days=31)).strftime('%Y-%m-%d'),
            'budget': 150.00
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Advertisement.objects.filter(title='New Test Ad').exists())
    
    def test_advertisement_detail_view_unauthenticated(self):
        """Test that the advertisement detail view redirects unauthenticated users"""
        response = self.client.get(reverse('advertisements:advertisement_detail', args=[self.ad.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_advertisement_detail_view_authenticated_non_staff(self):
        """Test that the advertisement detail view redirects non-staff users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('advertisements:advertisement_detail', args=[self.ad.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to admin login
    
    def test_advertisement_detail_view_authenticated_staff(self):
        """Test that the advertisement detail view works for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('advertisements:advertisement_detail', args=[self.ad.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')
    
    def test_edit_advertisement_view_get_authenticated_staff(self):
        """Test that the edit advertisement view returns a 200 response for staff users"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.get(reverse('advertisements:edit_advertisement', args=[self.ad.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Advertisement')
    
    def test_edit_advertisement_view_post_authenticated_staff(self):
        """Test that a staff user can edit an advertisement"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.post(reverse('advertisements:edit_advertisement', args=[self.ad.id]), {
            'title': 'Updated Test Ad',
            'description': 'This is an updated test advertisement',
            'image_url': 'https://example.com/updated-ad.jpg',
            'target_url': 'https://example.com/updated',
            'start_date': self.ad.start_date.strftime('%Y-%m-%d'),
            'end_date': self.ad.end_date.strftime('%Y-%m-%d'),
            'budget': 200.00
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Test Ad')
        self.assertEqual(self.ad.budget, 200.00)
    
    def test_delete_advertisement_view_post_authenticated_staff(self):
        """Test that a staff user can delete an advertisement"""
        self.client.login(email='admin@example.com', password='testpass123')
        response = self.client.post(reverse('advertisements:delete_advertisement', args=[self.ad.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(Advertisement.objects.filter(id=self.ad.id).exists())
