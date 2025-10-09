from django.urls import path
from .views import (
    QuizListCreateView, QuizDetailView, QuizTakeView, MyQuizAttemptsView,
    AssignmentListCreateView, AssignmentDetailView, AssignmentSubmitView,
    AssignmentGradeView, MyAssignmentsView
)

urlpatterns = [
    # Quiz endpoints
    path('courses/<int:course_id>/quizzes/', QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:quiz_id>/take/', QuizTakeView.as_view(), name='quiz-take'),
    path('my-attempts/', MyQuizAttemptsView.as_view(), name='my-quiz-attempts'),
    
    # Assignment endpoints
    path('courses/<int:course_id>/assignments/', AssignmentListCreateView.as_view(), name='assignment-list-create'),
    path('assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<int:assignment_id>/submit/', AssignmentSubmitView.as_view(), name='assignment-submit'),
    path('submissions/<int:submission_id>/grade/', AssignmentGradeView.as_view(), name='assignment-grade'),
    path('my-assignments/', MyAssignmentsView.as_view(), name='my-assignments'),
]
