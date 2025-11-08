from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from materials.models import Course, Lesson
from materials.serializers import (
    CourseSerializer, CourseDetailSerializer,
    LessonSerializer, LessonDetailSerializer
)
from materials.paginators import CoursePagination, LessonPagination
from users.permissions import IsModerator, IsOwner
from config.tasks import send_course_update_notification_with_throttling


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course model providing full CRUD operations
    Following instruction.txt requirements for permissions
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        Moderators: can view/edit, but not create/delete
        Owners: can view/edit/delete their own courses
        """
        if self.action == 'create':
            # Only authenticated non-moderators can create
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['destroy']:
            # Only owners can delete (moderators cannot)
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            # Moderators OR owners can view/edit
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'list':
            # All authenticated users can list
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Automatically assign the current user as owner when creating"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Save course and trigger async notification with throttling"""
        course = serializer.save()
        # Send async notification with 4-hour throttling
        send_course_update_notification_with_throttling.delay(course.id)

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        """Get queryset with prefetched lessons for performance"""
        return Course.objects.prefetch_related('lessons')

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Get all lessons for a specific course"""
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Generic view for listing and creating lessons
    Following instruction.txt requirements for permissions
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPagination
    permission_classes = [IsAuthenticated, ~IsModerator]  # Non-moderators can create

    def perform_create(self, serializer):
        """Automatically assign the current user as owner when creating"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Get queryset with selected related course for performance"""
        return Lesson.objects.select_related('course')


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic view for retrieving, updating, and deleting lessons
    Following instruction.txt requirements for permissions
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

    def perform_update(self, serializer):
        """Save lesson and trigger async course notification with throttling"""
        lesson = serializer.save()
        # Send async notification for the course with 4-hour throttling
        send_course_update_notification_with_throttling.delay(lesson.course.id)

    def get_queryset(self):
        """Get queryset with selected related course for performance"""
        return Lesson.objects.select_related('course')
