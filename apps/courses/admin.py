# Save as: apps/courses/admin.py

from django.contrib import admin
from .models import Category, Course, Module, Lesson, Enrollment, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'status', 'difficulty', 'price', 'is_free', 'created_at']
    list_filter = ['status', 'difficulty', 'is_free', 'category']
    search_fields = ['title', 'description', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course']
    search_fields = ['title', 'course__title']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'content_type', 'order', 'is_preview', 'created_at']
    list_filter = ['content_type', 'is_preview']
    search_fields = ['title', 'module__title']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'progress_percentage', 'completed', 'enrolled_at']
    list_filter = ['completed', 'enrolled_at']
    search_fields = ['student__email', 'course__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'student', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['course__title', 'student__email']
