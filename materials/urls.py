from django.urls import path, include
from rest_framework.routers import DefaultRouter
from materials.views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView
)

app_name = 'materials'

# Router for ViewSet (Course)
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    # ViewSet URLs (automatically generated)
    path('', include(router.urls)),
    
    # Generic class URLs for Lessons
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
]