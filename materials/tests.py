from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from materials.models import Course, Lesson
from materials.validators import validate_youtube_url

User = get_user_model()


class CourseModelTest(TestCase):
    """Test cases for Course model following TDD approach"""

    def test_create_course_successful(self):
        """Test creating a course is successful"""
        course = Course.objects.create(
            title='Python Fundamentals',
            description='Learn Python basics',
        )
        
        self.assertEqual(course.title, 'Python Fundamentals')
        self.assertEqual(course.description, 'Learn Python basics')
        self.assertEqual(str(course), 'Python Fundamentals')
        
    def test_course_title_required(self):
        """Test that course title is required"""
        with self.assertRaises(ValidationError):
            course = Course(description='Test description')
            course.full_clean()


class LessonModelTest(TestCase):
    """Test cases for Lesson model following TDD approach"""
    
    def setUp(self):
        """Create test course for lessons"""
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )

    def test_create_lesson_successful(self):
        """Test creating a lesson is successful"""
        lesson = Lesson.objects.create(
            title='Lesson 1: Variables',
            description='Learn about variables',
            course=self.course,
            video_url='https://youtube.com/watch?v=example'
        )
        
        self.assertEqual(lesson.title, 'Lesson 1: Variables')
        self.assertEqual(lesson.description, 'Learn about variables')
        self.assertEqual(lesson.course, self.course)
        self.assertEqual(lesson.video_url, 'https://youtube.com/watch?v=example')
        self.assertEqual(str(lesson), 'Lesson 1: Variables')
        
    def test_lesson_belongs_to_course(self):
        """Test that lesson belongs to a course"""
        lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test description',
            course=self.course
        )
        
        self.assertEqual(lesson.course, self.course)
        self.assertIn(lesson, self.course.lessons.all())
        
    def test_lesson_title_required(self):
        """Test that lesson title is required"""
        with self.assertRaises(ValidationError):
            lesson = Lesson(course=self.course, description='Test')
            lesson.full_clean()


class YouTubeValidatorTest(TestCase):
    """Test cases for YouTube URL validator"""
    
    def test_valid_youtube_urls(self):
        """Test that valid YouTube URLs pass validation"""
        valid_urls = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtu.be/dQw4w9WgXcQ',
            'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                # Should not raise ValidationError
                validate_youtube_url(url)
    
    def test_invalid_youtube_urls(self):
        """Test that non-YouTube URLs fail validation"""
        invalid_urls = [
            'https://vimeo.com/123456',
            'https://example.com/video',
            'https://twitch.tv/streamer',
            'https://dailymotion.com/video/123',
            'not_a_url',
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValidationError):
                    validate_youtube_url(url)
    
    def test_empty_url(self):
        """Test that empty URL doesn't raise error"""
        validate_youtube_url('')
        validate_youtube_url(None)


class LessonCRUDAPITest(APITestCase):
    """Test CRUD operations for Lesson API"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com', 
            password='testpass123'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        
        # Create test lesson
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test lesson description',
            course=self.course,
            video_url='https://youtube.com/watch?v=test',
            owner=self.user
        )
        
    def test_lesson_list_requires_authentication(self):
        """Test that lesson list requires authentication"""
        url = reverse('materials:lesson-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_lesson_list_authenticated(self):
        """Test authenticated user can list lessons"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lesson-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)  # Pagination
    
    def test_lesson_create_success(self):
        """Test creating a lesson successfully"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'New lesson description',
            'course': self.course.id,
            'video_url': 'https://youtube.com/watch?v=new'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
    
    def test_lesson_create_invalid_url(self):
        """Test creating lesson with invalid video URL fails"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'New lesson description',
            'course': self.course.id,
            'video_url': 'https://vimeo.com/invalid'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_lesson_retrieve(self):
        """Test retrieving a specific lesson"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lesson-detail', kwargs={'pk': self.lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.lesson.title)
    
    def test_lesson_update_owner(self):
        """Test owner can update their lesson"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lesson-detail', kwargs={'pk': self.lesson.id})
        data = {
            'title': 'Updated Lesson',
            'description': 'Updated description',
            'course': self.course.id,
            'video_url': 'https://youtube.com/watch?v=updated'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')
    
    def test_lesson_delete_owner(self):
        """Test owner can delete their lesson"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lesson-detail', kwargs={'pk': self.lesson.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)
    
    def test_lesson_update_other_user_forbidden(self):
        """Test other user cannot update lesson"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('materials:lesson-detail', kwargs={'pk': self.lesson.id})
        data = {'title': 'Hacked Lesson'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


