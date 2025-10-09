```python
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import Category, Course, Module, Lesson, Enrollment, LessonProgress, Review
from .serializers import (CategorySerializer, CourseListSerializer, CourseDetailSerializer,
                          ModuleSerializer, LessonSerializer, EnrollmentSerializer,
                          LessonProgressSerializer, ReviewSerializer)
from apps.authentication.permissions import IsInstructorUser, IsOwnerOrReadOnly

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'instructor__username']
    ordering_fields = ['created_at', 'price', 'title']
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published').select_related('instructor', 'category')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by price
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')
        
        return queryset


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(status='published')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class InstructorCourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class InstructorCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = [IsInstructorUser]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class ModuleListCreateView(generics.ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        course_slug = self.kwargs['course_slug']
        return Module.objects.filter(course__slug=course_slug, course__instructor=self.request.user)
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'], instructor=self.request.user)
        serializer.save(course=course)


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        return Module.objects.filter(course__instructor=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        module_id = self.kwargs['module_id']
        return Lesson.objects.filter(module_id=module_id, module__course__instructor=self.request.user)
    
    def perform_create(self, serializer):
        module = get_object_or_404(Module, id=self.kwargs['module_id'], course__instructor=self.request.user)
        serializer.save(module=module)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        return Lesson.objects.filter(module__course__instructor=self.request.user)


class EnrollCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug, status='published')
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({'error': 'Already enrolled in this course'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if course is free or payment is completed (simplified for now)
        if not course.is_free:
            # In real implementation, verify payment here
            return Response({'error': 'Payment required'}, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        enrollment = Enrollment.objects.create(student=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course')


class LessonProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.module.course)
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        # Update progress
        progress.completed = request.data.get('completed', progress.completed)
        progress.time_spent_seconds = request.data.get('time_spent_seconds', progress.time_spent_seconds)
        progress.last_position_seconds = request.data.get('last_position_seconds', progress.last_position_seconds)
        
        if progress.completed and not progress.completed_at:
            progress.completed_at = timezone.now()
        
        progress.save()
        
        # Update enrollment progress
        self.update_enrollment_progress(enrollment)
        
        serializer = LessonProgressSerializer(progress)
        return Response(serializer.data)
    
    def update_enrollment_progress(self, enrollment):
        total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
        if total_lessons == 0:
            return
        
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()
        
        progress_percentage = (completed_lessons / total_lessons) * 100
        enrollment.progress_percentage = progress_percentage
        
        if progress_percentage == 100 and not enrollment.completed:
            enrollment.completed = True
            enrollment.completed_at = timezone.now()
            
            # Award points to student
            enrollment.student.points += 100
            enrollment.student.save()
        
        enrollment.save()


class CourseReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        course_slug = self.kwargs['course_slug']
        return Review.objects.filter(course__slug=course_slug).select_related('student')
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        
        # Check if user is enrolled
        if not Enrollment.objects.filter(student=self.request.user, course=course).exists():
            raise permissions.PermissionDenied("You must be enrolled to review this course")
        
        serializer.save(student=self.request.user, course=course)


class MyCourseProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_slug):
        enrollment = get_object_or_404(Enrollment, student=request.user, course__slug=course_slug)
        
        progress_data = []
        modules = Module.objects.filter(course=enrollment.course).prefetch_related('lessons')
        
        for module in modules:
            module_data = {
                'module_id': module.id,
                'module_title': module.title,
                'lessons': []
            }
            
            for lesson in module.lessons.all():
                lesson_progress = LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson=lesson
                ).first()
                
                module_data['lessons'].append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'completed': lesson_progress.completed if lesson_progress else False,
                    'time_spent_seconds': lesson_progress.time_spent_seconds if lesson_progress else 0,
                    'last_position_seconds': lesson_progress.last_position_seconds if lesson_progress else 0,
                })
            
            progress_data.append(module_data)
        
        return Response({
            'enrollment': EnrollmentSerializer(enrollment).data,
            'progress': progress_data
        })
```
