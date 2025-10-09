```python
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
import joblib

User = get_user_model()

class CourseRecommendationEngine:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def prepare_data(self):
        """Prepare user-course interaction matrix"""
        enrollments = Enrollment.objects.all().values('student_id', 'course_id', 'progress_percentage', 'completed')
        
        if not enrollments:
            return None, None
        
        df = pd.DataFrame(enrollments)
        
        # Create user-course matrix
        matrix = df.pivot_table(
            index='student_id',
            columns='course_id',
            values='progress_percentage',
            fill_value=0
        )
        
        return matrix, df
    
    def train(self):
        """Train collaborative filtering model"""
        matrix, df = self.prepare_data()
        
        if matrix is None:
            return False
        
        # Normalize data
        matrix_normalized = self.scaler.fit_transform(matrix)
        
        # Train KNN model
        self.model = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.model.fit(matrix_normalized)
        
        return True
    
    def get_recommendations(self, user_id, n_recommendations=5):
        """Get course recommendations for a user"""
        matrix, df = self.prepare_data()
        
        if matrix is None or user_id not in matrix.index:
            # Return popular courses for new users
            return self.get_popular_courses(n_recommendations)
        
        # Get user vector
        user_vector = matrix.loc[user_id].values.reshape(1, -1)
        user_vector_normalized = self.scaler.transform(user_vector)
        
        # Find similar users
        distances, indices = self.model.kneighbors(user_vector_normalized)
        
        # Get courses from similar users
        similar_users = matrix.index[indices[0][1:]]  # Exclude the user itself
        
        # Find courses that similar users liked but current user hasn't taken
        enrolled_courses = set(Enrollment.objects.filter(student_id=user_id).values_list('course_id', flat=True))
        
        recommended_courses = []
        for similar_user in similar_users:
            user_courses = matrix.loc[similar_user]
            top_courses = user_courses[user_courses > 50].sort_values(ascending=False)
            
            for course_id, score in top_courses.items():
                if course_id not in enrolled_courses and course_id not in recommended_courses:
                    recommended_courses.append(course_id)
                
                if len(recommended_courses) >= n_recommendations:
                    break
            
            if len(recommended_courses) >= n_recommendations:
                break
        
        return Course.objects.filter(id__in=recommended_courses[:n_recommendations])
    
    def get_popular_courses(self, n=5):
        """Get most popular courses"""
        from django.db.models import Count
        
        popular = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).filter(status='published').order_by('-enrollment_count')[:n]
        
        return popular
    
    def get_personalized_learning_path(self, user_id, course_id):
        """Adjust learning path based on user performance"""
        from apps.assessments.models import QuizAttempt
        from apps.courses.models import Module, Lesson
        
        # Get user's quiz performance
        attempts = QuizAttempt.objects.filter(
            student_id=user_id,
            quiz__course_id=course_id
        ).order_by('-completed_at')
        
        if not attempts.exists():
            return self.get_standard_path(course_id)
        
        # Calculate average score
        avg_score = sum([a.score for a in attempts if a.score]) / len(attempts)
        
        # Adjust difficulty
        modules = Module.objects.filter(course_id=course_id).prefetch_related('lessons')
        
        learning_path = []
        for module in modules:
            lessons = list(module.lessons.all())
            
            if avg_score < 60:
                # Struggling: Add more foundational content
                learning_path.extend([l for l in lessons if l.is_preview or 'intro' in l.title.lower()])
            elif avg_score > 85:
                # Advanced: Skip basics, focus on advanced
                learning_path.extend([l for l in lessons if 'advanced' in l.title.lower() or l.order > len(lessons)/2])
            else:
                # Normal progression
                learning_path.extend(lessons)
        
        return learning_path
    
    def get_standard_path(self, course_id):
        """Get standard learning path"""
        from apps.courses.models import Lesson
        return Lesson.objects.filter(module__course_id=course_id).order_by('module__order', 'order')
```
