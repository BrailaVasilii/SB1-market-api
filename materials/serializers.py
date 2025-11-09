from rest_framework import serializers
from materials.models import Course, Lesson
from materials.validators import validate_youtube_url, YouTubeURLValidator
from typing import Dict, Any


class LessonForCourseSerializer(serializers.ModelSerializer):
    """Simplified serializer for lessons when displayed within course"""
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url']


class LessonSerializer(serializers.ModelSerializer):
    """Full serializer for Lesson model"""
    
    video_url = serializers.URLField(
        required=False, 
        allow_blank=True,
        validators=[validate_youtube_url]
    )
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'preview', 
            'video_url', 'course', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        validators = [YouTubeURLValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model with nested lessons"""
    
    lessons = LessonForCourseSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'preview',
            'lessons_count', 'lessons', 'is_subscribed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def get_lessons_count(self, obj: Course) -> int:
        """Get count of lessons in the course"""
        return obj.lessons.count()
    
    def get_is_subscribed(self, obj: Course) -> bool:
        """Check if current user is subscribed to this course"""
        # Subscriptions not implemented in SB1 Market API
        return False


class CourseDetailSerializer(CourseSerializer):
    """Detailed serializer for Course with full lesson info"""
    
    class Meta(CourseSerializer.Meta):
        pass


class LessonDetailSerializer(LessonSerializer):
    """Detailed serializer for Lesson with course info"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + ['course_title']