from rest_framework.pagination import PageNumberPagination


class AdvertisementPagination(PageNumberPagination):
    """
    Пагинация для объявлений
    SB1 Requirement: 4 items per page
    """
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100