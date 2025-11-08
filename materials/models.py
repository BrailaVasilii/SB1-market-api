from django.db import models
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()


class Course(models.Model):
    """Course model for LMS platform"""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    preview = models.ImageField(upload_to='courses/previews/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        return self.title


class Lesson(models.Model):
    """Lesson model for LMS platform"""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    preview = models.ImageField(upload_to='lessons/previews/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='lessons'
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['created_at']
        
    def __str__(self) -> str:
        return self.title
