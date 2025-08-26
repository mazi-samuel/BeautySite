from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import UserProfile, UserKYC, UserVerification

User = get_user_model()


class AccountsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='buyer'
        )
    
    def test_user_creation(self):
        """Test that a user can be created"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.user_type, 'buyer')
    
    def test_user_profile_creation(self):
        """Test that a user profile is created automatically"""
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)
    
    def test_user_kyc_creation(self):
        """Test that a user KYC can be created"""
        kyc = UserKYC.objects.create(
            user=self.user,
            id_document_url='https://example.com/id.jpg',
            selfie_url='https://example.com/selfie.jpg',
            status='pending'
        )
        self.assertEqual(kyc.user, self.user)
        self.assertEqual(kyc.status, 'pending')
    
    def test_user_verification_creation(self):
        """Test that a user verification can be created"""
        verification = UserVerification.objects.create(
            user=self.user,
            age_verified=True,
            age_verified_at=timezone.now()
        )
        self.assertEqual(verification.user, self.user)
        self.assertTrue(verification.age_verified)


class AccountsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_register_view_get(self):
        """Test that the register view returns a 200 response"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
    
    def test_register_view_post(self):
        """Test that a user can register"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'user_type': 'buyer'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_view_get(self):
        """Test that the login view returns a 200 response"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post(self):
        """Test that a user can login"""
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_profile_view_authenticated(self):
        """Test that the profile view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')
    
    def test_profile_view_unauthenticated(self):
        """Test that the profile view redirects unauthenticated users"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_kyc_submit_view_authenticated(self):
        """Test that the KYC submit view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('accounts:kyc_submit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Submit KYC Documents')
    
    def test_kyc_status_view_authenticated(self):
        """Test that the KYC status view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('accounts:kyc_status'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'KYC Verification Status')
    
    def test_age_verification_view_authenticated(self):
        """Test that the age verification view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('accounts:age_verification'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Age Verification')
