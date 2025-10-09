```python
from django.db import models
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Lesson
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=30)
    passing_score = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_attempts = models.IntegerField(default=3)
    show_answers = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=False)
    is_proctored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='mcq')
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'answers'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question.question_text[:50]} - {self.answer_text[:30]}"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.quiz.title} - Attempt {self.attempt_number}"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.FloatField(default=0)
    
    class Meta:
        db_table = 'student_answers'
    
    def __str__(self):
        return f"{self.attempt.student.email} - {self.question.question_text[:50]}"


class Assignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_points = models.IntegerField(default=100)
    submission_file_required = models.BooleanField(default=True)
    allow_late_submission = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assignments'
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    submission_text = models.TextField(blank=True)
    submission_file = models.FileField(upload_to='assignment_submissions/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'assignment_submissions'
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.assignment.title}"


class QuestionBank(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='question_bank')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=Question.QUESTION_TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    tags = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_bank'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.question_text[:50]}"
```
