from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import CommunityRoom, CommunityPost, CommunityMessage
from apps.accounts.models import UserVerification

User = get_user_model()


class CommunityModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.room = CommunityRoom.objects.create(
            name='Test Room',
            description='This is a test room',
            created_by=self.user
        )
    
    def test_community_room_creation(self):
        """Test that a community room can be created"""
        self.assertEqual(self.room.name, 'Test Room')
        self.assertEqual(self.room.description, 'This is a test room')
        self.assertEqual(self.room.created_by, self.user)
        self.assertFalse(self.room.is_private)
        self.assertFalse(self.room.is_adult_content)
    
    def test_community_post_creation(self):
        """Test that a community post can be created"""
        post = CommunityPost.objects.create(
            room=self.room,
            user=self.user,
            title='Test Post',
            content='This is a test post'
        )
        self.assertEqual(post.room, self.room)
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.content, 'This is a test post')
    
    def test_community_message_creation(self):
        """Test that a community message can be created"""
        post = CommunityPost.objects.create(
            room=self.room,
            user=self.user,
            title='Test Post',
            content='This is a test post'
        )
        message = CommunityMessage.objects.create(
            post=post,
            user=self.user,
            content='This is a test message'
        )
        self.assertEqual(message.post, post)
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.content, 'This is a test message')


class CommunityViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.room = CommunityRoom.objects.create(
            name='Test Room',
            description='This is a test room',
            created_by=self.user
        )
        self.post = CommunityPost.objects.create(
            room=self.room,
            user=self.user,
            title='Test Post',
            content='This is a test post'
        )
    
    def test_community_home_view(self):
        """Test that the community home view returns a 200 response"""
        response = self.client.get(reverse('community:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beauty Community')
    
    def test_rooms_view_unauthenticated(self):
        """Test that the rooms view redirects unauthenticated users"""
        response = self.client.get(reverse('community:rooms'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_rooms_view_authenticated(self):
        """Test that the rooms view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:rooms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Community Rooms')
    
    def test_room_detail_view_unauthenticated(self):
        """Test that the room detail view redirects unauthenticated users"""
        response = self.client.get(reverse('community:room_detail', args=[self.room.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_room_detail_view_authenticated(self):
        """Test that the room detail view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:room_detail', args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Room')
    
    def test_create_room_view_get_authenticated(self):
        """Test that the create room view returns a 200 response for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:create_room'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Room')
    
    def test_create_room_view_post_authenticated(self):
        """Test that an authenticated user can create a room"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('community:create_room'), {
            'name': 'New Test Room',
            'description': 'This is a new test room',
            'is_private': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(CommunityRoom.objects.filter(name='New Test Room').exists())
    
    def test_create_post_view_get_authenticated(self):
        """Test that the create post view returns a 200 response for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:create_post', args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Post')
    
    def test_create_post_view_post_authenticated(self):
        """Test that an authenticated user can create a post"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('community:create_post', args=[self.room.id]), {
            'title': 'New Test Post',
            'content': 'This is a new test post'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(CommunityPost.objects.filter(title='New Test Post').exists())
    
    def test_post_detail_view_unauthenticated(self):
        """Test that the post detail view redirects unauthenticated users"""
        response = self.client.get(reverse('community:post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_post_detail_view_authenticated(self):
        """Test that the post detail view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
    
    def test_add_message_view_post_authenticated(self):
        """Test that an authenticated user can add a message"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('community:add_message', args=[self.post.id]), {
            'content': 'This is a test message'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful addition
        self.assertTrue(CommunityMessage.objects.filter(content='This is a test message').exists())
    
    def test_private_messages_view_authenticated(self):
        """Test that the private messages view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:private_messages'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Private Messages')
    
    def test_private_message_thread_view_authenticated(self):
        """Test that the private message thread view works for authenticated users"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:private_message_thread', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Messages with')


class CommunityAdultContentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.adult_room = CommunityRoom.objects.create(
            name='Adult Room',
            description='This is an adult content room',
            created_by=self.user,
            is_adult_content=True
        )
        UserVerification.objects.create(
            user=self.user,
            age_verified=True,
            age_verified_at=timezone.now()
        )
    
    def test_adult_room_access_verified_user(self):
        """Test that verified users can access adult content rooms"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('community:room_detail', args=[self.adult_room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Adult Room')
    
    def test_adult_room_access_unverified_user(self):
        """Test that unverified users cannot access adult content rooms"""
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='testpass123'
        )
        self.client.login(email='unverified@example.com', password='testpass123')
        response = self.client.get(reverse('community:room_detail', args=[self.adult_room.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to age verification
