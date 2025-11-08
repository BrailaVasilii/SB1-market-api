from rest_framework.pagination import PageNumberPagination


class MaterialsPagination(PageNumberPagination):
    """
    Custom pagination for materials (courses and lessons).
    Allows client to control page size within reasonable limits.
    """
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to override page size
    max_page_size = 50  # Maximum allowed page size
    
    
class LessonPagination(PageNumberPagination):
    """
    Specific pagination for lessons with smaller page size.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class CoursePagination(PageNumberPagination):
    """
    Specific pagination for courses.
    """
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 30