```python
from django.urls import path
from .views import (
    CourseAnalyticsView, StudentEngagementView, CourseRecommendationsView,
    PersonalizedLearningPathView, InstructorDashboardView, StudentDashboardView
)

urlpatterns = [
    path('courses/<int:course_id>/analytics/', CourseAnalyticsView.as_view(), name='course-analytics'),
    path('courses/<int:course_id>/engagement/', StudentEngagementView.as_view(), name='student-engagement'),
    path('recommendations/', CourseRecommendationsView.as_view(), name='course-recommendations'),
    path('courses/<int:course_id>/learning-path/', PersonalizedLearningPathView.as_view(), name='learning-path'),
    path('instructor/dashboard/', InstructorDashboardView.as_view(), name='instructor-dashboard'),
    path('student/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
]
```
