```python
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Sum
from .models import CourseAnalytics, StudentEngagement
from .serializers import CourseAnalyticsSerializer, StudentEngagementSerializer
from .ml_engine import CourseRecommendationEngine
from apps.courses.models import Course, Enrollment
from apps.courses.serializers import CourseListSerializer
from apps.authentication.permissions import IsInstructorUser

class CourseAnalyticsView(APIView):
    permission_classes = [IsInstructorUser]
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        
        enrollments = Enrollment.objects.filter(course=course)
        
        analytics = {
            'total_enrollments': enrollments.count(),
            'total_completions': enrollments.filter(completed=True).count(),
            'average_progress': enrollments.aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0,
            'average_rating': course.average_rating,
            'completion_rate': (enrollments.filter(completed=True).count() / enrollments.count() * 100) if enrollments.count() > 0 else 0,
        }
        
        return Response(analytics)


class StudentEngagementView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        engagement, created = StudentEngagement.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        serializer = StudentEngagementSerializer(engagement)
        return Response(serializer.data)


class CourseRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        engine = CourseRecommendationEngine()
        
        # Try to train and get personalized recommendations
        if engine.train():
            recommended_courses = engine.get_recommendations(request.user.id, n_recommendations=10)
        else:
            # Fallback to popular courses
            recommended_courses = engine.get_popular_courses(n=10)
        
        serializer = CourseListSerializer(recommended_courses, many=True)
        return Response(serializer.data)


class PersonalizedLearningPathView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        engine = CourseRecommendationEngine()
        learning_path = engine.get_personalized_learning_path(request.user.id, course_id)
        
        from apps.courses.serializers import LessonSerializer
        serializer = LessonSerializer(learning_path, many=True)
        return Response(serializer.data)


class InstructorDashboardView(APIView):
    permission_classes = [IsInstructorUser]
    
    def get(self, request):
        courses = Course.objects.filter(instructor=request.user)
        
        dashboard_data = []
        for course in courses:
            enrollments = Enrollment.objects.filter(course=course)
            
            course_data = {
                'course_id': course.id,
                'course_title': course.title,
                'total_enrollments': enrollments.count(),
                'active_students': enrollments.filter(last_accessed__gte=timezone.now() - timedelta(days=7)).count(),
                'completion_rate': (enrollments.filter(completed=True).count() / enrollments.count() * 100) if enrollments.count() > 0 else 0,
                'average_progress': enrollments.aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0,
                'average_rating': course.average_rating,
            }
            
            dashboard_data.append(course_data)
        
        return Response(dashboard_data)


class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from datetime import timedelta
        from django.utils import timezone
        
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        
        dashboard_data = {
            'total_courses': enrollments.count(),
            'completed_courses': enrollments.filter(completed=True).count(),
            'in_progress_courses': enrollments.filter(completed=False).count(),
            'total_points': request.user.points,
            'recent_activity': [],
        }
        
        for enrollment in enrollments[:5]:
            dashboard_data['recent_activity'].append({
                'course_title': enrollment.course.title,
                'progress': enrollment.progress_percentage,
                'last_accessed': enrollment.last_accessed,
            })
        
        return Response(dashboard_data)
```
