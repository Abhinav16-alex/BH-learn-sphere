```python
from django.db import models
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Lesson

User = get_user_model()

class CourseAnalytics(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='analytics')
    total_enrollments = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    average_completion_rate = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_analytics'
    
    def __str__(self):
        return f"Analytics: {self.course.title}"


class StudentEngagement(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_metrics')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_engagements')
    total_time_spent_minutes = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    quizzes_taken = models.IntegerField(default=0)
    forum_posts = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    engagement_score = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'student_engagement'
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


class LessonAnalytics(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='analytics')
    total_views = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    average_time_spent_minutes = models.FloatField(default=0.0)
    drop_off_rate = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'lesson_analytics'
    
    def __str__(self):
        return f"Analytics: {self.lesson.title}"
```
