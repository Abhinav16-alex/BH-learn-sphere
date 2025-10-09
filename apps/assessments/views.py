```python
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Avg
from .models import Quiz, Question, Answer, QuizAttempt, StudentAnswer, Assignment, AssignmentSubmission
from .serializers import (QuizSerializer, QuestionSerializer, QuizAttemptSerializer,
                          StudentAnswerSerializer, AssignmentSerializer, AssignmentSubmissionSerializer)
from apps.courses.models import Course, Enrollment
from apps.authentication.permissions import IsInstructorUser

class QuizListCreateView(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Quiz.objects.filter(course_id=course_id, course__instructor=self.request.user)
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_id'], instructor=self.request.user)
        serializer.save(course=course)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        return Quiz.objects.filter(course__instructor=self.request.user)


class QuizTakeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Check enrollment
        if not Enrollment.objects.filter(student=request.user, course=quiz.course).exists():
            return Response({'error': 'You must be enrolled in this course'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check attempts
        attempts_count = QuizAttempt.objects.filter(quiz=quiz, student=request.user).count()
        if attempts_count >= quiz.max_attempts:
            return Response({'error': 'Maximum attempts reached'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            attempt_number=attempts_count + 1
        )
        
        serializer = QuizSerializer(quiz)
        return Response({
            'attempt_id': attempt.id,
            'quiz': serializer.data
        })
    
    def post(self, request, quiz_id):
        # Submit quiz answers
        attempt_id = request.data.get('attempt_id')
        answers = request.data.get('answers', [])
        
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user, quiz_id=quiz_id)
        
        if attempt.completed_at:
            return Response({'error': 'Quiz already submitted'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_points = 0
        earned_points = 0
        
        for answer_data in answers:
            question = get_object_or_404(Question, id=answer_data['question_id'], quiz=attempt.quiz)
            total_points += question.points
            
            student_answer = StudentAnswer.objects.create(
                attempt=attempt,
                question=question
            )
            
            if question.question_type in ['mcq', 'true_false']:
                selected_answer = get_object_or_404(Answer, id=answer_data['answer_id'])
                student_answer.selected_answer = selected_answer
                student_answer.is_correct = selected_answer.is_correct
                if selected_answer.is_correct:
                    student_answer.points_earned = question.points
                    earned_points += question.points
            else:
                student_answer.text_answer = answer_data.get('text_answer', '')
                # Manual grading required for text answers
                student_answer.is_correct = None
            
            student_answer.save()
        
        # Calculate score
        if total_points > 0:
            score = (earned_points / total_points) * 100
        else:
            score = 0
        
        attempt.score = score
        attempt.passed = score >= attempt.quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Award points if passed
        if attempt.passed:
            request.user.points += 50
            request.user.save()
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)


class MyQuizAttemptsView(generics.ListAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user).select_related('quiz')


class AssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Assignment.objects.filter(course_id=course_id, course__instructor=self.request.user)
    
    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs['course_id'], instructor=self.request.user)
        serializer.save(course=course)


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsInstructorUser]
    
    def get_queryset(self):
        return Assignment.objects.filter(course__instructor=self.request.user)


class AssignmentSubmitView(generics.CreateAPIView):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        assignment_id = self.kwargs['assignment_id']
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check enrollment
        if not Enrollment.objects.filter(student=self.request.user, course=assignment.course).exists():
            raise permissions.PermissionDenied("You must be enrolled in this course")
        
        # Check if already submitted
        if AssignmentSubmission.objects.filter(assignment=assignment, student=self.request.user).exists():
            raise serializers.ValidationError("Assignment already submitted")
        
        serializer.save(student=self.request.user, assignment=assignment)


class AssignmentGradeView(APIView):
    permission_classes = [IsInstructorUser]
    
    def post(self, request, submission_id):
        submission = get_object_or_404(
            AssignmentSubmission, 
            id=submission_id, 
            assignment__course__instructor=request.user
        )
        
        submission.grade = request.data.get('grade')
        submission.feedback = request.data.get('feedback', '')
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save()
        
        serializer = AssignmentSubmissionSerializer(submission)
        return Response(serializer.data)


class MyAssignmentsView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        enrolled_courses = Enrollment.objects.filter(student=self.request.user).values_list('course_id', flat=True)
        return Assignment.objects.filter(course_id__in=enrolled_courses)
```
