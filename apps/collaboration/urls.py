### **apps/collaboration/urls.py**
```python
from django.urls import path
from .views import (
    ForumListCreateView, ForumThreadListCreateView, ForumThreadDetailView,
    ForumPostCreateView, ChatRoomView, PeerReviewCreateView, LiveSessionListCreateView
)

urlpatterns = [
    # Forum
    path('courses/<int:course_id>/forums/', ForumListCreateView.as_view(), name='forum-list-create'),
    path('forums/<int:forum_id>/threads/', ForumThreadListCreateView.as_view(), name='thread-list-create'),
    path('threads/<int:pk>/', ForumThreadDetailView.as_view(), name='thread-detail'),
    path('threads/<int:thread_id>/posts/', ForumPostCreateView.as_view(), name='post-create'),
    
    # Chat
    path('courses/<int:course_id>/chat/', ChatRoomView.as_view(), name='chat-room'),
    
    # Peer Review
    path('peer-reviews/', PeerReviewCreateView.as_view(), name='peer-review-create'),
    
    # Live Sessions
    path('courses/<int:course_id>/live-sessions/', LiveSessionListCreateView.as_view(), name='live-session-list-create'),
]
```
