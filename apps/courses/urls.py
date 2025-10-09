```python
from django.urls import path
from .views import (
    CategoryListView, CourseListView, CourseDetailView,
    InstructorCourseListCreateView, InstructorCourseDetailView,
    ModuleListCreateView, ModuleDetailView,
    LessonListCreateView, LessonDetailView,
    EnrollCourseView, MyEnrollmentsView,
    LessonProgressView, CourseReviewView, MyCourseProgressView
)

urlpatterns = [
    # Public endpoints
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('', CourseListView.as_view(), name='course-list'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course-detail'),
    path('<slug:course_slug>/reviews/', CourseReviewView.as_view(), name='course-reviews'),
    
    # Instructor endpoints
    path('instructor/courses/', InstructorCourseListCreateView.as_view(), name='instructor-courses'),
    path('instructor/courses/<slug:slug>/', InstructorCourseDetailView.as_view(), name='instructor-course-detail'),
    path('instructor/<slug:course_slug>/modules/', ModuleListCreateView.as_view(), name='module-list-create'),
    path('instructor/modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),
    path('instructor/modules/<int:module_id>/lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('instructor/lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    
    # Student endpoints
    path('<slug:course_slug>/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('student/enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('student/lessons/<int:lesson_id>/progress/', LessonProgressView.as_view(), name='lesson-progress'),
    path('student/<slug:course_slug>/progress/', MyCourseProgressView.as_view(), name='my-course-progress'),
]
```
