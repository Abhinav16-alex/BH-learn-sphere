
```python
from rest_framework import serializers
from .models import CourseAnalytics, StudentEngagement, LessonAnalytics

class CourseAnalyticsSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseAnalytics
        fields = '__all__'


class StudentEngagementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = StudentEngagement
        fields = '__all__'


class LessonAnalyticsSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonAnalytics
        fields = '__all__'
```
