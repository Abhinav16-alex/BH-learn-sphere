### **apps/authentication/urls.py**
```python
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, BadgeListView, UserBadgesView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('badges/', BadgeListView.as_view(), name='badges'),
    path('my-badges/', UserBadgesView.as_view(), name='my-badges'),
]
```
