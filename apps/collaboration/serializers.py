```python
from rest_framework import serializers
from .models import Forum, ForumThread, ForumPost, ChatRoom, ChatMessage, PeerReview, LiveSession

class ForumSerializer(serializers.ModelSerializer):
    thread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Forum
        fields = '__all__'
    
    def get_thread_count(self, obj):
        return obj.threads.count()


class ForumPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = ForumPost
        fields = '__all__'
        read_only_fields = ['author', 'created_at', 'updated_at']


class ForumThreadSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    posts = ForumPostSerializer(many=True, read_only=True)
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumThread
        fields = '__all__'
        read_only_fields = ['author', 'views_count', 'created_at', 'updated_at']
    
    def get_post_count(self, obj):
        return obj.posts.count()


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['sender', 'timestamp']


class PeerReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    
    class Meta:
        model = PeerReview
        fields = '__all__'
        read_only_fields = ['reviewer', 'created_at']


class LiveSessionSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    
    class Meta:
        model = LiveSession
        fields = '__all__'
        read_only_fields = ['instructor', 'created_at']
```
