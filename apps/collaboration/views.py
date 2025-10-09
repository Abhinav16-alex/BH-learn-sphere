### **apps/collaboration/views.py**
```python
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Forum, ForumThread, ForumPost, ChatRoom, ChatMessage, PeerReview, LiveSession
from .serializers import (ForumSerializer, ForumThreadSerializer, ForumPostSerializer,
                          ChatMessageSerializer, PeerReviewSerializer, LiveSessionSerializer)
from apps.courses.models import Course, Enrollment

class ForumListCreateView(generics.ListCreateAPIView):
    serializer_class = ForumSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Forum.objects.filter(course_id=course_id)
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        serializer.save(course=course)


class ForumThreadListCreateView(generics.ListCreateAPIView):
    serializer_class = ForumThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        forum_id = self.kwargs.get('forum_id')
        return ForumThread.objects.filter(forum_id=forum_id)
    
    def perform_create(self, serializer):
        forum = get_object_or_404(Forum, id=self.kwargs['forum_id'])
        serializer.save(forum=forum, author=self.request.user)


class ForumThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ForumThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ForumThread.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ForumPostCreateView(generics.CreateAPIView):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        thread = get_object_or_404(ForumThread, id=self.kwargs['thread_id'])
        serializer.save(thread=thread, author=self.request.user)


class ChatRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        # Check enrollment
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            if course.instructor != request.user:
                return Response({'error': 'Not enrolled'}, status=403)
        
        chat_room, created = ChatRoom.objects.get_or_create(course=course)
        messages = ChatMessage.objects.filter(room=chat_room).select_related('sender')[:50]
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response({
            'room_id': chat_room.id,
            'messages': serializer.data
        })


class PeerReviewCreateView(generics.CreateAPIView):
    serializer_class = PeerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class LiveSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = LiveSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return LiveSession.objects.filter(course_id=course_id)
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        serializer.save(course=course, instructor=self.request.user)
```
