```python
from django.db import models
from django.contrib.auth import get_user_model
from apps.courses.models import Course

User = get_user_model()

class Forum(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forums'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class ForumThread(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_threads')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_threads'
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return self.title


class ForumPost(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    is_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_posts'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.thread.title} - Post by {self.author.email}"


class ChatRoom(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_rooms'
    
    def __str__(self):
        return f"Chat: {self.course.title}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.email}: {self.message[:50]}"


class PeerReview(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    
    assignment_submission = models.ForeignKey('assessments.AssignmentSubmission', on_delete=models.CASCADE, related_name='peer_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_reviews_given')
    rating = models.IntegerField()
    feedback = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'peer_reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer.email}"


class LiveSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_sessions')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_sessions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'live_sessions'
        ordering = ['scheduled_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
```
