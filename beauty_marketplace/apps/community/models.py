from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class CommunityRoom(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    is_adult_content = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class CommunityPost(models.Model):
    room = models.ForeignKey(CommunityRoom, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    has_media = models.BooleanField(default=False)
    media_url = models.URLField(blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class CommunityMessage(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    has_media = models.BooleanField(default=False)
    media_url = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Message by {self.user.username} on {self.post.title}"
